// src/pages/api/auth/login.ts
import type { APIRoute } from "astro";
import { supabase } from "../../../lib/supabase";

export const GET: APIRoute = async () => {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: "google",
    options: {
      redirectTo: "https://cctymkglaybpynkshzen.supabase.co/auth/v1/callback", // cambia en producción
    },
  });

  if (error) {
    return new Response("Error starting Google login", { status: 500 });
  }

  return Response.redirect(data.url, 302); // Redirige a Google
};
