// src/pages/api/auth/login.ts - Usando cliente centralizado
import type { APIRoute } from "astro";
import { supabase } from "../../../lib/supabase";

export const GET: APIRoute = async () => {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: "google",
    options: {
      // ✅ Redirigir directamente a tu app
      redirectTo: "http://localhost:4321/auth-complete",
      queryParams: {
        access_type: 'offline',
        prompt: 'consent',
      }
    },
  });

  if (error) {
    console.error('❌ Error iniciando OAuth:', error.message);
    return new Response("Error starting Google login", { status: 500 });
  }

  console.log('🚀 Redirigiendo a Google OAuth:', data.url);
  return Response.redirect(data.url, 302);
};