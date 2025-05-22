import type { APIRoute } from "astro";
import { supabase } from "../../../lib/supabase";

export const GET: APIRoute = async ({ url, cookies, redirect }) => {
  const code = url.searchParams.get("code");

  if (code) {
    const { data, error } = await supabase.auth.exchangeCodeForSession(code);
    
    if (!error && data.session) {
      const { access_token, refresh_token } = data.session;
      
      cookies.set("sb-access-token", access_token, {
        path: "/",
        httpOnly: true,
        sameSite: "lax",
        maxAge: 60 * 60 * 24 * 7
      });
      
      cookies.set("sb-refresh-token", refresh_token, {
        path: "/",
        httpOnly: true,
        sameSite: "lax",
        maxAge: 60 * 60 * 24 * 30
      });

      return redirect("/dashboard");
    }
  }

  return redirect("/signin?error=Unable to authenticate");
};