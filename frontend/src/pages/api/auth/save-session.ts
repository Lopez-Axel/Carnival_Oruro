// src/pages/api/auth/save-session.ts - Usando cliente centralizado
import type { APIRoute } from "astro";
import { supabase } from "../../../lib/supabase";

export const POST: APIRoute = async ({ request, cookies }) => {
  console.log('💾 Guardando sesión...');
  
  try {
    const { access_token, refresh_token, expires_at } = await request.json();
    
    if (!access_token || !refresh_token) {
      console.log('❌ Tokens faltantes');
      return new Response('Tokens requeridos', { status: 400 });
    }
    
    console.log('🔑 Tokens recibidos para guardar');
    
    // Verificar que los tokens sean válidos usando el cliente centralizado
    const { data, error } = await supabase.auth.setSession({
      access_token,
      refresh_token
    });
    
    if (error) {
      console.error('❌ Error validando tokens:', error.message);
      return new Response('Tokens inválidos: ' + error.message, { status: 400 });
    }
    
    if (!data.user) {
      console.error('❌ No se pudo obtener usuario');
      return new Response('No se pudo obtener usuario', { status: 400 });
    }
    
    console.log('✅ Tokens válidos para usuario:', data.user.email);
    
    const isProduction = import.meta.env.PROD;
    
    // Establecer cookies seguras
    cookies.set("sb-access-token", access_token, {
      path: "/",
      httpOnly: true,
      secure: isProduction,
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 7 // 7 días
    });
    
    cookies.set("sb-refresh-token", refresh_token, {
      path: "/",
      httpOnly: true,
      secure: isProduction,
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 30 // 30 días
    });
    
    console.log('🍪 Cookies establecidas exitosamente');
    
    return new Response(JSON.stringify({ 
      success: true, 
      user: {
        id: data.user.id,
        email: data.user.email,
        name: data.user.user_metadata?.full_name || data.user.email
      }
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
  } catch (error) {
    console.error('💥 Error en save-session:', error);
    return new Response('Error interno: ' + error, { status: 500 });
  }
};