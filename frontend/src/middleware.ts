// src/middleware.ts
import { defineMiddleware } from 'astro:middleware';
import { supabase, getCurrentUser, type UserProfile } from './lib/supabase';

// Rutas que requieren autenticación
const protectedRoutes = ['/dashboard', '/admin', '/vendedor', '/profile'];

// Rutas que requieren roles específicos
const roleRoutes: Record<string, UserProfile['role'][]> = {
  '/admin': ['administrador'],
  '/vendedor': ['vendedor', 'administrador'],
  '/dashboard': ['cliente', 'vendedor', 'administrador']
};

export const onRequest = defineMiddleware(async (context, next) => {
  const { request, cookies, redirect, url } = context;
  
  // Obtener tokens de las cookies
  const accessToken = cookies.get('sb-access-token')?.value;
  const refreshToken = cookies.get('sb-refresh-token')?.value;

  // Si hay tokens, establecer la sesión en Supabase
  if (accessToken && refreshToken) {
    await supabase.auth.setSession({
      access_token: accessToken,
      refresh_token: refreshToken
    });
  }

  // Verificar si la ruta actual requiere autenticación
  const pathname = url.pathname;
  const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route));
  
  if (isProtectedRoute) {
    const currentUser = await getCurrentUser();
    
    // Si no hay usuario autenticado, redirigir al login
    if (!currentUser) {
      return redirect('/signin');
    }

    // Verificar roles específicos
    const requiredRoles = roleRoutes[pathname] || roleRoutes[Object.keys(roleRoutes).find(route => pathname.startsWith(route)) || ''];
    
    if (requiredRoles && currentUser.profile) {
      if (!requiredRoles.includes(currentUser.profile.role)) {
        return redirect('/dashboard'); // o página de "no autorizado"
      }
    }

    // Agregar información del usuario al contexto local
    context.locals.user = currentUser;
  }

  // Si el usuario ya está autenticado y trata de acceder a login/registro, redirigir al dashboard
  if ((pathname === '/signin' || pathname === '/signup') && accessToken) {
    const currentUser = await getCurrentUser();
    if (currentUser) {
      return redirect('/dashboard');
    }
  }

  return next();
});

// Agregar tipos para el contexto local
declare global {
  namespace App {
    interface Locals {
      user?: {
        user: any;
        profile: UserProfile | null;
      };
    }
  }
}