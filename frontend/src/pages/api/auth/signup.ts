import type { APIRoute } from "astro";
import { supabase } from "../../../lib/supabase";

export const POST: APIRoute = async ({ request, redirect }) => {
  try {
    const formData = await request.formData();
    const email = formData.get("email")?.toString();
    const password = formData.get("password")?.toString();
    const fullName = formData.get("fullName")?.toString();
    const role = formData.get("role")?.toString() as 'cliente' | 'vendedor' | 'administrador';

    if (!email || !password) {
      return new Response("Email and password are required", { status: 400 });
    }

    // Registrar usuario en Supabase Auth
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName || email,
          role: role || 'cliente'
        }
      }
    });

    if (error) {
      console.error("Supabase signup error:", error.message);
      return new Response(error.message, { status: 500 });
    }

    // Si el usuario fue creado exitosamente, el trigger automáticamente creará el perfil
    return redirect("/signin?message=Check your email for verification");
  } catch (err: any) {
    console.error("Unexpected error:", err);
    return new Response("Internal server error", { status: 500 });
  }
};