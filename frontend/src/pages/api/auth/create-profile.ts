// src/pages/api/auth/create-profile.ts
import type { APIRoute } from "astro";
import { supabase } from "../../../lib/supabase";

export const POST: APIRoute = async ({ request }) => {
  console.log('👤 Creando perfil de usuario...');
  
  try {
    const { userId, email, fullName, role = 'cliente' } = await request.json();
    
    if (!userId || !email) {
      return new Response('Usuario ID y email son requeridos', { status: 400 });
    }
    
    console.log('📝 Datos para crear perfil:', { userId, email, fullName, role });
    
    // Verificar si el perfil ya existe
    const { data: existingProfile, error: checkError } = await supabase
      .from('user_profiles')
      .select('id')
      .eq('id', userId)
      .single();
    
    if (existingProfile) {
      console.log('⚠️ El perfil ya existe');
      return new Response('El perfil ya existe', { status: 409 });
    }
    
    // Crear el perfil
    const { data, error } = await supabase
      .from('user_profiles')
      .insert({
        id: userId,
        email: email,
        full_name: fullName || email,
        role: role,
        is_active: true
      })
      .select()
      .single();
    
    if (error) {
      console.error('❌ Error creando perfil:', error);
      return new Response('Error creando perfil: ' + error.message, { status: 500 });
    }
    
    console.log('✅ Perfil creado exitosamente:', data);
    
    return new Response(JSON.stringify({ 
      success: true, 
      profile: data 
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
  } catch (error) {
    console.error('💥 Error inesperado:', error);
    return new Response('Error interno del servidor', { status: 500 });
  }
};