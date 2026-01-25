import resend
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_password_reset_email(user_email, user_name, uid, token):
    """
    Envía correo de recuperación de contraseña con enlace de reseteo
    
    Args:
        user_email: Email del usuario
        user_name: Nombre del usuario
        uid: UID codificado del usuario
        token: Token de reseteo
    
    Returns:
        dict: Resultado del envío
    """
    try:
        resend.api_key = settings.RESEND_API_KEY
        
        # Construir el enlace de reseteo
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">Recuperación de Contraseña</h1>
            </div>
            
            <div style="padding: 40px 30px;">
                <p style="font-size: 16px;">Hola <strong>{user_name}</strong>,</p>
                
                <p style="font-size: 16px;">
                    Recibimos una solicitud para restablecer la contraseña de tu cuenta en el Sistema de Reclutamiento.
                </p>
                
                <div style="background-color: #f8f9fa; border-left: 4px solid #667eea; padding: 20px; margin: 30px 0;">
                    <p style="margin: 0; font-size: 14px; color: #666;">
                        ⚠️ Si no solicitaste este cambio, puedes ignorar este correo de forma segura.
                    </p>
                </div>
                
                <p style="font-size: 16px;">
                    Para establecer una nueva contraseña, haz clic en el siguiente botón:
                </p>
                
                <div style="text-align: center; margin: 40px 0;">
                    <a href="{reset_link}" 
                       style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                              color: white; padding: 16px 40px; text-decoration: none; border-radius: 8px; 
                              font-weight: bold; font-size: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        🔒 Recuperar Contraseña
                    </a>
                </div>
                
                <div style="background-color: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 8px; margin: 30px 0;">
                    <p style="margin: 0; font-size: 14px; color: #856404;">
                        <strong>⏰ Importante:</strong> Este enlace expirará en <strong>1 hora</strong>.
                    </p>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    Si el botón no funciona, copia y pega este enlace en tu navegador:
                </p>
                <p style="font-size: 12px; color: #667eea; word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 4px;">
                    {reset_link}
                </p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #dee2e6;">
                <p style="margin: 0; font-size: 14px; color: #666;">
                    Sistema de Reclutamiento - <strong>adrestalent.com</strong>
                </p>
                <p style="margin: 10px 0 0 0; font-size: 12px; color: #999;">
                    Si tienes problemas, contáctanos: soporte@adrestalent.com
                </p>
            </div>
        </body>
        </html>
        """
        
        params = {
            "from": settings.FROM_EMAIL,
            "to": [user_email],
            "subject": "Recuperación de Contraseña - Sistema de Reclutamiento",
            "html": html_content,
        }
        
        response = resend.Emails.send(params)
        logger.info(f"✅ Email de recuperación enviado a {user_email}")
        
        return {
            "success": True,
            "email_id": response.get('id'),
            "message": "Email enviado exitosamente"
        }
        
    except Exception as e:
        logger.error(f"❌ Error enviando email de recuperación a {user_email}: {str(e)}")
        return {
            "success": False,
            "message": f"Error al enviar email: {str(e)}"
        }


def send_password_reset_confirmation(user_email, user_name):
    """
    Envía correo de confirmación después de cambiar la contraseña exitosamente
    
    Args:
        user_email: Email del usuario
        user_name: Nombre del usuario
    
    Returns:
        dict: Resultado del envío
    """
    try:
        resend.api_key = settings.RESEND_API_KEY
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">✅ Contraseña Actualizada</h1>
            </div>
            
            <div style="padding: 40px 30px;">
                <p style="font-size: 16px;">Hola <strong>{user_name}</strong>,</p>
                
                <div style="background-color: #d1fae5; border-left: 4px solid #10b981; padding: 20px; margin: 30px 0;">
                    <p style="margin: 0; font-size: 16px; color: #065f46;">
                        ✅ Tu contraseña ha sido cambiada exitosamente.
                    </p>
                </div>
                
                <p style="font-size: 16px;">
                    Tu contraseña del Sistema de Reclutamiento ha sido actualizada correctamente. 
                    Ya puedes iniciar sesión con tu nueva contraseña.
                </p>
                
                <div style="background-color: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 8px; margin: 30px 0;">
                    <p style="margin: 0; font-size: 14px; color: #856404;">
                        <strong>⚠️ Importante:</strong> Si no realizaste este cambio, contacta inmediatamente 
                        a nuestro equipo de soporte.
                    </p>
                </div>
                
                <div style="text-align: center; margin: 40px 0;">
                    <a href="{settings.FRONTEND_URL}/login" 
                       style="display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                              color: white; padding: 16px 40px; text-decoration: none; border-radius: 8px; 
                              font-weight: bold; font-size: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        🔐 Iniciar Sesión
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    Recomendaciones de seguridad:
                </p>
                <ul style="font-size: 14px; color: #666;">
                    <li>No compartas tu contraseña con nadie</li>
                    <li>Usa una contraseña única y segura</li>
                    <li>Actualiza tu contraseña periódicamente</li>
                </ul>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #dee2e6;">
                <p style="margin: 0; font-size: 14px; color: #666;">
                    Sistema de Reclutamiento - <strong>adrestalent.com</strong>
                </p>
                <p style="margin: 10px 0 0 0; font-size: 12px; color: #999;">
                    Si tienes problemas, contáctanos: soporte@adrestalent.com
                </p>
            </div>
        </body>
        </html>
        """
        
        params = {
            "from": settings.FROM_EMAIL,
            "to": [user_email],
            "subject": "Contraseña Actualizada Exitosamente - Sistema de Reclutamiento",
            "html": html_content,
        }
        
        response = resend.Emails.send(params)
        logger.info(f"✅ Email de confirmación enviado a {user_email}")
        
        return {
            "success": True,
            "email_id": response.get('id'),
            "message": "Email enviado exitosamente"
        }
        
    except Exception as e:
        logger.error(f"❌ Error enviando email de confirmación a {user_email}: {str(e)}")
        return {
            "success": False,
            "message": f"Error al enviar email: {str(e)}"
        }
