// src/pages/api/auth/signup.ts - Usando cliente centralizado
import type { APIRoute } from "astro";
import { supabase } from "../../../lib/supabase";

export const POST: APIRoute = async ({ request, redirect }) => {
  console.log('📝 Iniciando proceso de registro');
  
  try {
    const formData = await request.formData();
    const email = formData.get("email")?.toString();
    const password = formData.get("password")?.toString();
    const fullName = formData.get("fullName")?.toString();
    const role = formData.get("role")?.toString() as 'cliente';
    const phone = formData.get("phone")?.toString();

    if (!email || !password) {
      return redirect('/signup?error=' + encodeURIComponent('Email y contraseña son requeridos'));
    }

    if (!fullName) {
      return redirect('/signup?error=' + encodeURIComponent('El nombre completo es requerido'));
    }

    if (!role || !['cliente', 'vendedor'].includes(role)) {
      return redirect('/signup?error=' + encodeURIComponent('Debe seleccionar un tipo de cuenta válido'));
    }

    console.log('📧 Registrando usuario:', { email, fullName, role });

    // Registrar usuario en Supabase Auth usando el cliente centralizado
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
          role: role,
          phone: phone || null
        }
      }
    });

    if (error) {
      console.error('❌ Error de registro:', error.message);
      return redirect('/signup?error=' + encodeURIComponent(error.message));
    }

    if (!data.user) {
      console.error('❌ No se pudo crear el usuario');
      return redirect('/signup?error=' + encodeURIComponent('No se pudo crear el usuario'));
    }

    console.log('✅ Usuario registrado exitosamente:', data.user.email);

    // Si el usuario fue creado exitosamente, el trigger automáticamente creará el perfil
    if (data.session) {
      // Usuario confirmado automáticamente
      console.log('🎉 Usuario confirmado automáticamente, redirigiendo al dashboard');
      
      // Establecer cookies si hay sesión
      const { access_token, refresh_token } = data.session;
      const isProduction = import.meta.env.PROD;
      
      // No podemos establecer cookies en redirect, necesitamos usar otro enfoque
      return redirect('/signin?success=' + encodeURIComponent('Cuenta creada exitosamente. Por favor inicia sesión.'));
    } else {
      // Usuario necesita confirmar email
      console.log('📧 Enviado email de confirmación');
      return redirect('/signin?message=' + encodeURIComponent('Cuenta creada. Revisa tu email para confirmar tu cuenta antes de iniciar sesión.'));
    }

  } catch (err: any) {
    console.error('💥 Error inesperado en registro:', err);
    return redirect('/signup?error=' + encodeURIComponent('Error interno del servidor'));
  }
};