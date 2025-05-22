# backend/app/services/email_service.py
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, HtmlContent
from typing import List, Optional
import logging
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@carnaval-oruro.com")
        self.base_url = os.getenv("BASE_URL", "http://localhost:8000")  # URL base para enlaces
        
        # Validar configuración
        if not self.sendgrid_api_key:
            logger.warning("SENDGRID_API_KEY not configured - email functionality will be disabled")
            self.sg = None
        else:
            try:
                self.sg = SendGridAPIClient(api_key=self.sendgrid_api_key)
                logger.info("SendGrid email service initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing SendGrid: {e}")
                self.sg = None
    
    async def send_vendor_application_confirmation(
        self, 
        user_email: str, 
        user_name: str, 
        application_id: str
    ):
        """Envía confirmación de solicitud al usuario"""
        if not self.sg:
            logger.warning("Email service not available - skipping confirmation email")
            return
            
        subject = "✅ Solicitud de Vendedor Recibida - Carnaval de Oruro"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Solicitud Recibida</title>
        </head>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 12px 12px 0 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: white; margin: 0; font-size: 28px; font-weight: bold;">🎭 Carnaval de Oruro</h1>
                <p style="color: #f0f0f0; margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Sistema de Vendedores Autorizados</p>
            </div>
            
            <!-- Main Content -->
            <div style="background: white; padding: 40px 30px; border: none; border-radius: 0 0 12px 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #2563eb; margin-top: 0; font-size: 24px;">¡Solicitud Recibida Exitosamente! 🎉</h2>
                
                <p style="font-size: 16px; margin-bottom: 20px;">Hola <strong style="color: #1f2937;">{user_name}</strong>,</p>
                
                <p style="font-size: 16px; line-height: 1.7;">Hemos recibido tu solicitud para convertirte en vendedor autorizado del Carnaval de Oruro. ¡Gracias por tu interés en formar parte de nuestro equipo!</p>
                
                <!-- Status Card -->
                <div style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-left: 4px solid #2563eb; padding: 25px; margin: 30px 0; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <h3 style="margin: 0 0 15px 0; color: #1e40af; font-size: 18px;">📋 Detalles de tu Solicitud</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; font-weight: 600; color: #374151; width: 40%;">Número de solicitud:</td>
                            <td style="padding: 8px 0;"><code style="background: #e5e7eb; padding: 4px 8px; border-radius: 4px; font-family: 'Courier New', monospace; color: #1f2937;">{application_id}</code></td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: 600; color: #374151;">Estado:</td>
                            <td style="padding: 8px 0;"><span style="background: #fef3c7; color: #d97706; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 14px;">⏳ En revisión</span></td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: 600; color: #374151;">Fecha de envío:</td>
                            <td style="padding: 8px 0; color: #1f2937;">{self._get_current_date()}</td>
                        </tr>
                    </table>
                </div>
                
                <!-- Process Steps -->
                <h3 style="color: #374151; font-size: 20px; margin-bottom: 15px;">🔄 ¿Qué sigue ahora?</h3>
                <div style="background: #f9fafb; padding: 25px; border-radius: 10px; margin: 20px 0; border: 1px solid #e5e7eb;">
                    <ol style="margin: 0; padding-left: 0; list-style: none; counter-reset: step-counter;">
                        <li style="margin-bottom: 15px; padding-left: 40px; position: relative; counter-increment: step-counter;">
                            <span style="position: absolute; left: 0; top: 0; background: #2563eb; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px;">1</span>
                            <strong style="color: #1f2937;">Revisión de documentos:</strong> Nuestro equipo verificará la información y documentos que proporcionaste.
                        </li>
                        <li style="margin-bottom: 15px; padding-left: 40px; position: relative; counter-increment: step-counter;">
                            <span style="position: absolute; left: 0; top: 0; background: #2563eb; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px;">2</span>
                            <strong style="color: #1f2937;">Evaluación:</strong> Analizaremos tu solicitud basándose en nuestros criterios de selección.
                        </li>
                        <li style="margin-bottom: 15px; padding-left: 40px; position: relative; counter-increment: step-counter;">
                            <span style="position: absolute; left: 0; top: 0; background: #2563eb; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px;">3</span>
                            <strong style="color: #1f2937;">Decisión:</strong> Te notificaremos la decisión por email en un plazo de 3-5 días hábiles.
                        </li>
                        <li style="margin-bottom: 0; padding-left: 40px; position: relative; counter-increment: step-counter;">
                            <span style="position: absolute; left: 0; top: 0; background: #2563eb; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px;">4</span>
                            <strong style="color: #1f2937;">Activación:</strong> Si eres aprobado, recibirás acceso a tu panel de vendedor.
                        </li>
                    </ol>
                </div>
                
                <!-- Action Buttons -->
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{self.base_url}/dashboard" 
                       style="display: inline-block; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; padding: 14px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 8px; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3); transition: all 0.3s ease;">
                        📊 Ver Mi Dashboard
                    </a>
                    <a href="{self.base_url}/vendor/my-application" 
                       style="display: inline-block; background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%); color: white; padding: 14px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 8px; box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3);">
                        🔍 Estado de Solicitud
                    </a>
                </div>
                
                <!-- Contact Info -->
                <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border: 1px solid #f59e0b; padding: 20px; border-radius: 10px; margin: 30px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #92400e; font-size: 16px;">💬 ¿Tienes preguntas?</h4>
                    <p style="margin: 0; color: #92400e; line-height: 1.5;">
                        Contáctanos en <a href="mailto:soporte.carnaval.oruro@gmail.com" style="color: #d97706; font-weight: 600;">soporte.carnaval.oruro@gmail.com</a><br>
                        O por WhatsApp: <a href="https://wa.me/59170123456" style="color: #d97706; font-weight: 600;">+591 70123456</a>
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                    <p style="margin: 0; font-size: 16px; color: #1f2937;">¡Esperamos tenerte pronto como parte de nuestro equipo de vendedores autorizados!</p>
                    
                    <p style="margin-top: 20px; color: #6b7280;">
                        Saludos cordiales,<br>
                        <strong style="color: #1f2937;">Equipo Carnaval de Oruro</strong>
                    </p>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="text-align: center; padding: 25px 20px; color: #6b7280; font-size: 12px; background: #f8f9fa; margin-top: 20px; border-radius: 8px;">
                <p style="margin: 0 0 5px 0;">Este es un email automático, por favor no respondas a esta dirección.</p>
                <p style="margin: 0;">© 2025 Carnaval de Oruro. Todos los derechos reservados.</p>
            </div>
        </body>
        </html>
        """
        
        await self._send_email(user_email, subject, html_content)
    
    async def send_admin_notification(
        self, 
        admin_email: str, 
        application_id: str,
        business_name: str,
        applicant_name: str
    ):
        """Notifica a admin sobre nueva solicitud"""
        if not self.sg:
            logger.warning("Email service not available - skipping admin notification")
            return
            
        subject = f"🔔 Nueva Solicitud de Vendedor - {business_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Nueva Solicitud</title>
        </head>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
            
            <div style="background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color: white; padding: 25px; text-align: center; border-radius: 12px 12px 0 0; box-shadow: 0 2px 10px rgba(0,0,0,0.15);">
                <h2 style="margin: 0; font-size: 24px; font-weight: bold;">⚠️ Nueva Solicitud de Vendedor</h2>
                <p style="margin: 8px 0 0 0; opacity: 0.9;">Requiere revisión inmediata</p>
            </div>
            
            <div style="background: white; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border: 1px solid #fecaca; border-radius: 10px; padding: 25px; margin: 25px 0;">
                    <h3 style="margin: 0 0 20px 0; color: #dc2626; font-size: 18px; display: flex; align-items: center;">
                        📄 Detalles de la Solicitud
                    </h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px 0; font-weight: 600; color: #374151; width: 30%;">Solicitante:</td>
                            <td style="padding: 10px 0; color: #1f2937; font-weight: 500;">{applicant_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; font-weight: 600; color: #374151;">Negocio:</td>
                            <td style="padding: 10px 0; color: #1f2937; font-weight: 500;">{business_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; font-weight: 600; color: #374151;">ID Solicitud:</td>
                            <td style="padding: 10px 0;"><code style="background: #e5e7eb; padding: 4px 8px; border-radius: 4px; font-family: 'Courier New', monospace; color: #1f2937;">{application_id}</code></td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; font-weight: 600; color: #374151;">Fecha:</td>
                            <td style="padding: 10px 0; color: #1f2937;">{self._get_current_date()}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px 0; font-weight: 600; color: #374151;">Prioridad:</td>
                            <td style="padding: 10px 0;"><span style="background: #dc2626; color: white; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 12px;">🔥 ALTA</span></td>
                        </tr>
                    </table>
                </div>
                
                <p style="font-size: 16px; margin: 25px 0;">Una nueva solicitud de vendedor ha sido enviada y <strong>requiere tu revisión inmediata</strong>.</p>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{self.base_url}/admin/vendor-applications/{application_id}" 
                       style="display: inline-block; background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);">
                        🔍 Revisar Solicitud Ahora
                    </a>
                </div>
                
                <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #6b7280;">
                    <h4 style="margin: 0 0 10px 0; color: #374151; font-size: 14px;">⏰ Recordatorio Importante</h4>
                    <p style="margin: 0; font-size: 14px; color: #4b5563; line-height: 1.5;">
                        Las solicitudes deben revisarse dentro de las primeras <strong>24 horas</strong> para mantener un excelente servicio al cliente y cumplir con nuestros estándares de tiempo de respuesta.
                    </p>
                </div>
                
                <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); padding: 20px; border-radius: 8px; margin: 25px 0; border: 1px solid #93c5fd;">
                    <h4 style="margin: 0 0 10px 0; color: #1e40af; font-size: 14px;">📋 Checklist de Revisión</h4>
                    <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #1e40af;">
                        <li>Verificar documentos de identidad</li>
                        <li>Validar información comercial</li>
                        <li>Revisar experiencia y motivación</li>
                        <li>Confirmar datos de contacto</li>
                    </ul>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="text-align: center; padding: 20px; color: #6b7280; font-size: 12px; background: #f8f9fa; margin-top: 15px; border-radius: 8px;">
                <p style="margin: 0;">Panel de Administración - Carnaval de Oruro</p>
            </div>
        </body>
        </html>
        """
        
        await self._send_email(admin_email, subject, html_content)
    
    async def send_vendor_approval(
        self, 
        user_email: str, 
        user_name: str,
        business_name: str
    ):
        """Notifica aprobación de vendedor"""
        if not self.sg:
            logger.warning("Email service not available - skipping approval email")
            return
            
        subject = "🎉 ¡Solicitud Aprobada! - Vendedor Autorizado Carnaval de Oruro"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Solicitud Aprobada</title>
        </head>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f0fdf4;">
            
            <div style="background: linear-gradient(135deg, #059669 0%, #047857 100%); color: white; padding: 35px; text-align: center; border-radius: 12px 12px 0 0; box-shadow: 0 4px 20px rgba(5, 150, 105, 0.3);">
                <h1 style="margin: 0; font-size: 32px; font-weight: bold;">🎉 ¡Felicidades!</h1>
                <p style="margin: 15px 0 0 0; font-size: 18px; opacity: 0.95;">Tu solicitud ha sido aprobada</p>
            </div>
            
            <div style="background: white; padding: 40px 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
                <h2 style="color: #047857; margin-top: 0; font-size: 26px; text-align: center;">¡Bienvenido al Equipo! 🚀</h2>
                
                <p style="font-size: 16px; margin-bottom: 20px;">Hola <strong style="color: #1f2937;">{user_name}</strong>,</p>
                
                <p style="font-size: 16px; line-height: 1.7; margin-bottom: 25px;">¡Excelentes noticias! Tu solicitud para convertirte en vendedor autorizado del Carnaval de Oruro ha sido <strong style="color: #059669; background: #ecfdf5; padding: 2px 8px; border-radius: 4px;">APROBADA</strong>.</p>
                
                <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border: 1px solid #bbf7d0; border-radius: 12px; padding: 25px; margin: 30px 0; position: relative;">
                    <div style="position: absolute; top: -10px; left: 20px; background: #059669; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: bold;">✅ APROBADO</div>
                    <h3 style="margin: 10px 0 20px 0; color: #047857; font-size: 18px;">Estado de tu Cuenta</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; font-weight: 600; color: #374151; width: 40%;">Negocio:</td>
                            <td style="padding: 8px 0; color: #1f2937; font-weight: 500;">{business_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: 600; color: #374151;">Estado:</td>
                            <td style="padding: 8px 0;"><span style="background: #059669; color: white; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 14px;">🟢 Vendedor Autorizado</span></td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: 600; color: #374151;">Fecha de Activación:</td>
                            <td style="padding: 8px 0; color: #1f2937;">{self._get_current_date()}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: 600; color: #374151;">Comisión inicial:</td>
                            <td style="padding: 8px 0; color: #059669; font-weight: 600;">10% por venta</td>
                        </tr>
                    </table>
                </div>
                
                <h3 style="color: #374151; font-size: 20px; margin: 30px 0 15px 0;">🚀 Próximos Pasos</h3>
                <div style="background: #f9fafb; padding: 25px; border-radius: 10px; margin: 20px 0; border: 1px solid #e5e7eb;">
                    <ol style="margin: 0; padding-left: 0; list-style: none; counter-reset: step-counter;">
                        <li style="margin-bottom: 15px; padding-left: 40px; position: relative; counter-increment: step-counter;">
                            <span style="position: absolute; left: 0; top: 0; background: #059669; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px;">1</span>
                            <strong style="color: #1f2937;">Accede a tu Panel:</strong> Ya puedes iniciar sesión y acceder a todas las funcionalidades de vendedor.
                        </li>
                        <li style="margin-bottom: 15px; padding-left: 40px; position: relative; counter-increment: step-counter;">
                            <span style="position: absolute; left: 0; top: 0; background: #059669; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px;">2</span>
                            <strong style="color: #1f2937;">Configura tu Perfil:</strong> Actualiza tus métodos de pago y preferencias.
                        </li>
                        <li style="margin-bottom: 15px; padding-left: 40px; position: relative; counter-increment: step-counter;">
                            <span style="position: absolute; left: 0; top: 0; background: #059669; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px;">3</span>
                            <strong style="color: #1f2937;">Conoce las Entradas:</strong> Familiarízate con los diferentes tipos disponibles.
                        </li>
                        <li style="margin-bottom: 0; padding-left: 40px; position: relative; counter-increment: step-counter;">
                            <span style="position: absolute; left: 0; top: 0; background: #059669; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px;">4</span>
                            <strong style="color: #1f2937;">¡Comienza a Vender!</strong> Genera ventas y obtén comisiones.
                        </li>
                    </ol>
                </div>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{self.base_url}/vendor/dashboard" 
                       style="display: inline-block; background: linear-gradient(135deg, #059669 0%, #047857 100%); color: white; padding: 16px 40px; text-decoration: none; border-radius: 10px; font-weight: 600; font-size: 16px; box-shadow: 0 6px 20px rgba(5, 150, 105, 0.4); text-transform: uppercase; letter-spacing: 1px;">
                        🚀 Acceder a Mi Panel
                    </a>
                </div>
                
                <div style="background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); border: 1px solid #f59e0b; padding: 25px; border-radius: 10px; margin: 30px 0;">
                    <h4 style="margin: 0 0 15px 0; color: #92400e; font-size: 16px;">📋 Información Importante</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; color: #92400e;">
                        <div>
                            <strong>💰 Comisión:</strong><br>10% por cada venta
                        </div>
                        <div>
                            <strong>💳 Pagos:</strong><br>Procesados semanalmente
                        </div>
                        <div>
                            <strong>📚 Capacitación:</strong><br>En los próximos días
                        </div>
                        <div>
                            <strong>🆘 Soporte:</strong><br>Disponible 24/7
                        </div>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 2px solid #e5e7eb;">
                    <p style="font-size: 18px; color: #1f2937; margin-bottom: 15px;">¡Estamos emocionados de tenerte en nuestro equipo!</p>
                    <p style="font-size: 16px; color: #6b7280; margin-bottom: 20px;">Esperamos que tengas mucho éxito como vendedor autorizado del Carnaval de Oruro.</p>
                    
                    <p style="color: #6b7280;">
                        ¡Bienvenido a bordo! 🎊<br>
                        <strong style="color: #1f2937;">Equipo Carnaval de Oruro</strong><br>
                        <a href="mailto:soporte.carnaval.oruro@gmail.com" style="color: #059669; text-decoration: none;">soporte.carnaval.oruro@gmail.com</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        await self._send_email(user_email, subject, html_content)
    
    async def send_vendor_rejection(
        self, 
        user_email: str, 
        user_name: str,
        rejection_reason: str
    ):
        """Notifica rechazo de solicitud"""
        if not self.sg:
            logger.warning("Email service not available - skipping rejection email")
            return
            
        subject = "📋 Actualización de tu Solicitud - Carnaval de Oruro"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Actualización de Solicitud</title>
        </head>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #fefce8;">
            
            <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 30px; text-align: center; border-radius: 12px 12px 0 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="margin: 0; font-size: 24px; font-weight: bold;">📋 Actualización de tu Solicitud</h2>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Carnaval de Oruro - Sistema de Vendedores</p>
            </div>
            
            <div style="background: white; padding: 35px 30px; border-radius: 0 0 12px 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <p style="font-size: 16px; margin-bottom: 20px;">Hola <strong style="color: #1f2937;">{user_name}</strong>,</p>
                
                <p style="font-size: 16px; line-height: 1.7; margin-bottom: 25px;">Gracias por tu interés en convertirte en vendedor autorizado del Carnaval de Oruro. Hemos revisado cuidadosamente tu solicitud.</p>
                
                <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border: 1px solid #f59e0b; padding: 25px; border-radius: 10px; margin: 30px 0;">
                    <h3 style="margin: 0 0 15px 0; color: #92400e; font-size: 18px;">📊 Estado de tu Solicitud</h3>
                    <p style="margin: 0; color: #92400e; font-size: 16px;"><strong>En esta ocasión, no pudimos aprobar tu solicitud.</strong></p>
                </div>
                
                <h4 style="color: #374151; font-size: 18px; margin-bottom: 15px;">💬 Razón de la decisión:</h4>
                <div style="background: #f9fafb; border-left: 4px solid #6b7280; padding: 20px; margin: 20px 0; border-radius: 0 8px 8px 0;">
                    <p style="margin: 0; color: #4b5563; font-style: italic; font-size: 15px; line-height: 1.6;">"{rejection_reason}"</p>
                </div>
                
                <h4 style="color: #374151; font-size: 18px; margin: 30px 0 15px 0;">🔄 ¿Qué puedes hacer ahora?</h4>
                <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border: 1px solid #0ea5e9; padding: 25px; border-radius: 10px; margin: 20px 0;">
                    <ul style="margin: 0; padding-left: 20px; color: #0c4a6e; line-height: 1.7;">
                        <li style="margin-bottom: 12px;"><strong>Mejora los aspectos mencionados</strong> en la razón de rechazo</li>
                        <li style="margin-bottom: 12px;"><strong>Revisa nuestros requisitos</strong> y asegúrate de cumplir todos</li>
                        <li style="margin-bottom: 12px;"><strong>Puedes enviar una nueva solicitud</strong> en 30 días</li>
                        <li style="margin-bottom: 0;"><strong>Mientras tanto</strong>, puedes seguir comprando entradas como cliente</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{self.base_url}/vendor/requirements" 
                       style="display: inline-block; background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%); color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 8px; box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);">
                        📋 Ver Requisitos
                    </a>
                    <a href="mailto:soporte.carnaval.oruro@gmail.com" 
                       style="display: inline-block; background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%); color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 8px; box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3);">
                        💬 Contactar Soporte
                    </a>
                </div>
                
                <div style="background: #f8fafc; padding: 25px; border-radius: 10px; margin: 30px 0; border: 1px solid #e2e8f0;">
                    <h4 style="margin: 0 0 15px 0; color: #475569; font-size: 16px;">💡 Consejos para tu próxima solicitud:</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #64748b; line-height: 1.6;">
                        <li style="margin-bottom: 8px;">Asegúrate de completar todos los campos requeridos</li>
                        <li style="margin-bottom: 8px;">Proporciona documentos claros y legibles</li>
                        <li style="margin-bottom: 8px;">Explica detalladamente tu experiencia y motivación</li>
                        <li style="margin-bottom: 0;">Revisa toda la información antes de enviar</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 40px; padding-top: 25px; border-top: 1px solid #e5e7eb;">
                    <p style="font-size: 16px; color: #1f2937; margin-bottom: 15px;">Agradecemos tu interés y esperamos que consideres aplicar nuevamente en el futuro.</p>
                    
                    <p style="color: #6b7280;">
                        Saludos cordiales,<br>
                        <strong style="color: #1f2937;">Equipo Carnaval de Oruro</strong><br>
                        <a href="mailto:soporte.carnaval.oruro@gmail.com" style="color: #f59e0b; text-decoration: none;">soporte.carnaval.oruro@gmail.com</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        await self._send_email(user_email, subject, html_content)
    
    def _get_current_date(self) -> str:
        """Obtiene la fecha actual formateada en español"""
        months = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        ]
        
        now = datetime.now()
        month_name = months[now.month - 1]
        return f"{now.day} de {month_name} de {now.year}"
    
    async def _send_email(self, to_email: str, subject: str, html_content: str):
        """Método privado para enviar emails usando SendGrid"""
        if not self.sg:
            logger.error(f"Cannot send email to {to_email} - SendGrid not configured")
            return
            
        try:
            message = Mail(
                from_email=From(self.from_email, "Carnaval de Oruro"),
                to_emails=To(to_email),
                subject=Subject(subject),
                html_content=HtmlContent(html_content)
            )
            
            response = self.sg.send(message)
            
            if response.status_code in [200, 202]:
                logger.info(f"Email sent successfully to {to_email} - Status: {response.status_code}")
            else:
                logger.warning(f"Email send returned unexpected status {response.status_code} for {to_email}")
                
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            # No hacer raise para no bloquear el flujo principal
            # En producción, podrías implementar un sistema de retry o queue