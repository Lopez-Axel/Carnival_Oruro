import type { APIRoute } from "astro";
import { updateUserProfile, getCurrentUser } from "../../../lib/supabase";

export const PUT: APIRoute = async ({ request }) => {
  try {
    const currentUser = await getCurrentUser();
    
    if (!currentUser) {
      return new Response("Unauthorized", { status: 401 });
    }

    const updates = await request.json();
    const { data, error } = await updateUserProfile(currentUser.user.id, updates);

    if (error) {
      return new Response(error.message, { status: 500 });
    }

    return new Response(JSON.stringify(data), {
      headers: { "Content-Type": "application/json" }
    });
  } catch (err: any) {
    return new Response("Internal server error", { status: 500 });
  }
};