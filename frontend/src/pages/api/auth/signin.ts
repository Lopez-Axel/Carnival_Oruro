// src/pages/api/auth/signin.ts - Usando cliente centralizado
import type { APIRoute } from "astro";
import { supabase } from "../../../lib/supabase";

export const POST: APIRoute = async ({ request, cookies, redirect }) => {
  console.log('🔐 Iniciando proceso de login con email/password');
  
  const formData = await request.formData();
  const email = formData.get("email")?.toString();
  const password = formData.get("password")?.toString();

  if (!email || !password) {
    console.log('❌ Email o password faltante');
    return new Response("Email and password are required", { status: 400 });
  }

  console.log('📧 Intentando login para:', email);

  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (error) {
    console.error('❌ Error de Supabase:', error.message);
    return redirect(`/signin?error=${encodeURIComponent(error.message)}`);
  }

  if (!data.session) {
    console.error('❌ No se pudo crear la sesión');
    return redirect('/signin?error=' + encodeURIComponent('No se pudo iniciar sesión'));
  }

  console.log('✅ Login exitoso para:', email);
  console.log('🔑 Tokens obtenidos:', {
    hasAccessToken: !!data.session.access_token,
    hasRefreshToken: !!data.session.refresh_token,
    expiresAt: data.session.expires_at
  });

  const { access_token, refresh_token } = data.session;
  
  // Configurar cookies con opciones más seguras
  const isProduction = import.meta.env.PROD;
  
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

  console.log('🍪 Cookies establecidas, redirigiendo a dashboard');

  return redirect("/dashboard");
};