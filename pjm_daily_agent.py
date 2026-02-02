# pjm_daily_agent.py
import anthropic
import psycopg2
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_yesterday_prices():
    """Pull yesterday's PJM real-time prices from PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT', 5432),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        
        cur = conn.cursor()
        
        # First, check what dates we have available
        cur.execute("""
            SELECT DISTINCT timestamp::date as date
            FROM pjm_data.realtime_prices
            ORDER BY date DESC
            LIMIT 5
        """)
        available_dates = cur.fetchall()
        
        if not available_dates:
            print("❌ No data available in the database")
            conn.close()
            return None, None, None
        
        # Use the most recent date available
        latest_date = available_dates[0][0]
        print(f"📅 Most recent data available: {latest_date}")
        
        # Get comprehensive price data for analysis
        query = f"""
        SELECT 
            node_name,
            zone,
            lmp,
            energy_component,
            congestion_component,
            loss_component,
            timestamp
        FROM pjm_data.realtime_prices 
        WHERE timestamp::date = '{latest_date}'
        ORDER BY lmp DESC 
        LIMIT 100
        """
        
        cur.execute(query)
        results = cur.fetchall()
        
        # Get summary statistics by zone
        stats_query = f"""
        SELECT 
            zone,
            COUNT(*) as records,
            ROUND(AVG(lmp)::numeric, 2) as avg_lmp,
            ROUND(MAX(lmp)::numeric, 2) as max_lmp,
            ROUND(MIN(lmp)::numeric, 2) as min_lmp,
            ROUND(AVG(congestion_component)::numeric, 2) as avg_congestion,
            ROUND(MAX(congestion_component)::numeric, 2) as max_congestion
        FROM pjm_data.realtime_prices 
        WHERE timestamp::date = '{latest_date}'
        GROUP BY zone
        ORDER BY avg_lmp DESC
        """
        
        cur.execute(stats_query)
        zone_stats = cur.fetchall()
        
        conn.close()
        
        print(f"✅ Retrieved {len(results)} price records")
        print(f"📊 Analysis includes {len(zone_stats)} zones")
        
        return results, zone_stats, latest_date
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None, None, None

def analyze_with_claude(price_data, zone_stats, analysis_date):
    """Use Claude to analyze PJM market data"""
    if not price_data:
        return "No data available to analyze."
    
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Format data for Claude
    data_summary = f"PJM Real-Time Market Analysis - {analysis_date}\n"
    data_summary += "="*70 + "\n\n"
    
    # Top 15 highest LMP nodes
    data_summary += "🔥 TOP 15 HIGHEST LMP NODES:\n"
    for i, row in enumerate(price_data[:15], 1):
        node_name, zone, lmp, energy, congestion, loss, timestamp = row
        data_summary += f"{i:2d}. {node_name:20s} | Zone: {zone:6s} | "
        data_summary += f"LMP: ${float(lmp):7.2f} | "
        data_summary += f"Cong: ${float(congestion):6.2f} | "
        data_summary += f"Energy: ${float(energy):6.2f}\n"
    
    # Zone-level statistics
    data_summary += f"\n{'='*70}\n"
    data_summary += "📊 ZONE-LEVEL STATISTICS:\n"
    data_summary += f"{'Zone':<10} {'Records':<10} {'Avg LMP':<12} {'Max LMP':<12} {'Avg Cong':<12} {'Max Cong':<12}\n"
    data_summary += "-"*70 + "\n"
    
    for zone_data in zone_stats:
        zone, records, avg_lmp, max_lmp, min_lmp, avg_cong, max_cong = zone_data
        data_summary += f"{zone:<10} {records:<10} "
        data_summary += f"${float(avg_lmp):>9.2f}  "
        data_summary += f"${float(max_lmp):>9.2f}  "
        data_summary += f"${float(avg_cong):>9.2f}  "
        data_summary += f"${float(max_cong):>9.2f}\n"
    
    # Overall market statistics
    all_lmps = [float(row[2]) for row in price_data]
    all_congestion = [float(row[4]) for row in price_data]
    
    data_summary += f"\n{'='*70}\n"
    data_summary += "📈 OVERALL MARKET METRICS:\n"
    data_summary += f"Average LMP: ${sum(all_lmps)/len(all_lmps):.2f}/MWh\n"
    data_summary += f"Peak LMP: ${max(all_lmps):.2f}/MWh\n"
    data_summary += f"Average Congestion: ${sum(all_congestion)/len(all_congestion):.2f}/MWh\n"
    data_summary += f"Max Congestion: ${max(all_congestion):.2f}/MWh\n"
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{
            "role": "user", 
            "content": f"""Analyze this PJM real-time market data and provide:

1. **Price Spikes Analysis**: Identify nodes/zones with unusual LMP spikes and potential causes
2. **Congestion Hotspots**: Which areas showed significant congestion and why it matters
3. **Trading Opportunities**: Actionable insights for energy traders based on the patterns
4. **Zone Comparison**: Key differences between zones that traders should watch

{data_summary}

Keep it concise, focused on trading insights, and highlight anything unusual for PJM markets."""
        }]
    )
    
    return message.content[0].text

def save_report(analysis, analysis_date):
    """Save report to file"""
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    report_file = f"{reports_dir}/pjm_market_brief_{analysis_date.strftime('%Y%m%d')}.txt"
    
    with open(report_file, 'w') as f:
        f.write(f"PJM Real-Time Market Brief\n")
        f.write(f"Analysis Date: {analysis_date.strftime('%Y-%m-%d')}\n")
        f.write("="*70 + "\n\n")
        f.write(analysis)
        f.write(f"\n\n{'='*70}\n")
        f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    return report_file

def send_email(report_file, analysis, analysis_date):
    """Send email with the market brief report"""
    try:
        print("📧 Preparing email...")
        
        # Email configuration from .env
        email_from = os.getenv('EMAIL_FROM')
        email_password = os.getenv('EMAIL_PASSWORD')
        email_to = os.getenv('EMAIL_TO')
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        
        # Validate email configuration
        if not all([email_from, email_password, email_to]):
            print("❌ Email configuration missing in .env file")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = email_to
        msg['Subject'] = f"PJM Market Brief - {analysis_date.strftime('%B %d, %Y')}"
        
        # Email body
        body = f"""
Good morning,

Here's your automated PJM Market Intelligence Brief for {analysis_date.strftime('%B %d, %Y')}.

{analysis}

---
This report was automatically generated by your PJM Daily Agent.
Report file attached: {os.path.basename(report_file)}

Best regards,
PJM Market Intelligence Agent
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach the report file
        with open(report_file, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(report_file)}'
            )
            msg.attach(part)
        
        # Send email
        print(f"📤 Connecting to {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        print("🔐 Authenticating...")
        server.login(email_from, email_password)
        
        print(f"📨 Sending email to {email_to}...")
        text = msg.as_string()
        server.sendmail(email_from, email_to, text)
        server.quit()
        
        print(f"✅ Email sent successfully to {email_to}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

def main():
    print("🤖 Starting PJM Market Daily Agent...")
    
    # Get data
    prices, zone_stats, analysis_date = get_yesterday_prices()
    
    if not prices or not zone_stats:
        print("❌ No price data available. Exiting.")
        return
    
    # Analyze with Claude
    print("🧠 Analyzing with Claude API...")
    analysis = analyze_with_claude(prices, zone_stats, analysis_date)
    
    # Save report
    report_file = save_report(analysis, analysis_date)
    print(f"\n✅ Report saved: {report_file}")
    
    # Send email
    print(f"\n{'='*70}")
    email_sent = send_email(report_file, analysis, analysis_date)
    
    if email_sent:
        print(f"{'='*70}")
        print("🎉 Daily brief completed and emailed successfully!")
    else:
        print(f"{'='*70}")
        print("⚠️  Report generated but email failed. Check your email settings.")
    
    print(f"\n📄 REPORT PREVIEW:")
    print(f"{'='*70}\n")
    print(analysis[:500] + "...")
    print(f"\n{'='*70}")

if __name__ == "__main__":
    main()