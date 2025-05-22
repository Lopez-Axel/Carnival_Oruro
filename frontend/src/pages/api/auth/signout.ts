// src/pages/api/auth/signout.ts - Usando cliente centralizado
import type { APIRoute } from "astro";
import { supabase } from "../../../lib/supabase";

export const GET: APIRoute = async ({ cookies, redirect }) => {
  console.log('🚪 Iniciando proceso de logout');
  
  try {
    // Intentar cerrar sesión en Supabase (opcional, ya que no tenemos sesión activa en servidor)
    const { error } = await supabase.auth.signOut();
    
    if (error) {
      console.warn('⚠️ Error cerrando sesión en Supabase (no crítico):', error.message);
    }
    
    console.log('✅ Sesión cerrada en Supabase');
    
  } catch (err) {
    console.warn('⚠️ Error inesperado cerrando sesión (no crítico):', err);
  }
  
  // Limpiar cookies (esto es lo más importante)
  cookies.delete("sb-access-token", { path: "/" });
  cookies.delete("sb-refresh-token", { path: "/" });
  
  console.log('🍪 Cookies eliminadas');
  console.log('👋 Logout completado, redirigiendo a signin');
  
  return redirect("/signin?message=" + encodeURIComponent("Sesión cerrada correctamente"));
};