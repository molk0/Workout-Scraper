import smtplib, ssl
import config
import logging

context = ssl.create_default_context()


def send_mail(alert: str, receiver_email: str) -> None:
	"""Send an email to the given receiver email."""
	server = smtplib.SMTP('smtp.gmail.com', 587)
	try:
		server.starttls(context=context)
		server.login(config.SENDER_EMAIL, config.EMAIL_PASS)
		server.sendmail(config.SENDER_EMAIL, receiver_email, alert)
	except Exception as e:
		logging.exception(e)
	finally:
		server.quit()
