// src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.SUPABASE_URL;
const supabaseAnonKey = import.meta.env.SUPABASE_ANON_KEY;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Tipos TypeScript
export interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  role: 'cliente' | 'vendedor' | 'administrador';
  phone?: string;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthUser {
  user: any;
  profile: UserProfile | null;
}

// Función para obtener el perfil del usuario
export async function getUserProfile(userId: string): Promise<UserProfile | null> {
  const { data, error } = await supabase
    .from('user_profiles')
    .select('*')
    .eq('id', userId)
    .single();

  if (error) {
    console.error('Error fetching user profile:', error);
    return null;
  }

  return data;
}

// Función para actualizar el perfil del usuario
export async function updateUserProfile(userId: string, updates: Partial<UserProfile>) {
  const { data, error } = await supabase
    .from('user_profiles')
    .update(updates)
    .eq('id', userId)
    .select()
    .single();

  if (error) {
    console.error('Error updating user profile:', error);
    return { data: null, error };
  }

  return { data, error: null };
}

// Función para obtener usuario actual con perfil
export async function getCurrentUser(): Promise<AuthUser | null> {
  const { data: { user }, error } = await supabase.auth.getUser();
  
  if (error || !user) {
    return null;
  }

  const profile = await getUserProfile(user.id);
  
  return {
    user,
    profile
  };
}

// Función para verificar si el usuario tiene un rol específico
export async function hasRole(requiredRole: UserProfile['role']): Promise<boolean> {
  const currentUser = await getCurrentUser();
  
  if (!currentUser?.profile) {
    return false;
  }

  // Jerarquía de roles: administrador > vendedor > cliente
  const roleHierarchy = {
    'cliente': 1,
    'vendedor': 2,
    'administrador': 3
  };

  return roleHierarchy[currentUser.profile.role] >= roleHierarchy[requiredRole];
}