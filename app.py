import streamlit as st
import google.generativeai as genai
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
import os

# Set up your Gmail credentials here
GMAIL_USERNAME = "ramanandsabnis7@gmail.com"
GMAIL_PASSWORD = "uocn dyvn djwe bfcb"  # Use app-specific password if you have 2FA enabled

# Configure Gemini API
api_key = "AIzaSyAN9X21mRy4yIg2yG7RiLk0yIP3bP78G8M"  # Replace with your Gemini API key
genai.configure(api_key=api_key)

# Function to generate job description using Gemini API
def get_job_description(job_title, responsibilities, required_skills, preferred_skills, benefits):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    prompt = f"""
    Create a detailed job description for the following job title:
 
    Job Title: {job_title}
    Key Responsibilities: {responsibilities}
    Required Skills: {required_skills}
    Preferred Skills: {preferred_skills}
    Benefits Offered: {benefits}
    """
    response = model.generate_content(prompt)
    return response.text

# Function to generate PDF from the job description using ReportLab
def generate_pdf(description, job_title):
    pdf_filename = "job_description.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=A4)
    width, height = A4

    # Set up font for the title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 50, f"Job Description for: {job_title}")

    # Set up the styles for the paragraph (automatic text wrapping)
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    
    # Create a Paragraph object for the job description text
    paragraph = Paragraph(description, normal_style)
    
    # Get the position to start writing the text (below the title)
    y_position = height - 80

    # Define the available width for text
    width_available = width - 2 * 72  # Left and right margins (72 each)
    paragraph_width = width_available
    paragraph_height = paragraph.wrap(paragraph_width, height - 100)[1]  # Wrap text to fit on the page

    # Check if paragraph fits on the page, otherwise add new page
    if y_position - paragraph_height < 72:
        c.showPage()  # Add new page
        y_position = height - 50  # Reset the Y position

    # Draw the paragraph at the starting position
    paragraph.drawOn(c, 72, y_position - paragraph_height)

    # Save the PDF
    c.save()

    return pdf_filename

# Function to send email with the PDF attachment
def send_email(subject, body, sender_email, receiver_email, sender_password, pdf_file):
    try:
        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject

        # Attach the body of the email
        message.attach(MIMEText(body, 'plain'))

        # Attach the PDF file
        with open(pdf_file, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={pdf_file}')
            message.attach(part)

        # Establish SMTP connection using Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Start TLS encryption
        server.login(sender_email, sender_password)
        text = message.as_string()

        # Send email
        server.sendmail(sender_email, receiver_email, text)
        server.quit()  # Close the connection

        return "Email sent successfully!"
    except Exception as e:
        return f"Error: {e}"

# Streamlit UI
st.title("✨ Job Description Generator ✨")
st.markdown("Enter the job details below, and generate the job description. You can also save it as a PDF or send it via email.")

# Input for job details
job_title = st.text_input("What is the job title?")
responsibilities = st.text_area("List the key responsibilities:")
required_skills = st.text_input("List required skills (comma-separated):")
preferred_skills = st.text_input("List preferred skills (comma-separated):")
benefits = st.text_area("List the benefits offered:")

# Button to generate PDF when all details are entered
if job_title and responsibilities and required_skills and preferred_skills and benefits:
    # Generate job description from Gemini API
    job_description = get_job_description(job_title, responsibilities, required_skills, preferred_skills, benefits)

    # Generate PDF from the job description
    pdf_file = generate_pdf(job_description, job_title)

    # Button to save the PDF
    with open(pdf_file, "rb") as f:
        st.download_button(
            label="Download PDF",
            data=f,
            file_name=pdf_file,
            mime="application/pdf"
        )
    
    st.success("PDF generated successfully!")

    # Email sending functionality
    email_sender = st.text_input("Your Email (Gmail):")
    email_receiver = st.text_input("Receiver's Email:")

    send_email_button = st.button("Send Job Description via Email")
    if send_email_button:
        if email_sender and email_receiver:
            result = send_email("Job Description PDF", job_description, email_sender, email_receiver, GMAIL_PASSWORD, pdf_file)
            st.success(result)
        else:
            st.error("Please fill in both sender and receiver email.")
else:
    st.warning("Please fill in all the job details to generate the job description.")
