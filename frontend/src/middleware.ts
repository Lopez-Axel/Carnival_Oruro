// src/middleware.ts
import { defineMiddleware } from 'astro:middleware';
import { supabase, getCurrentUser, type UserProfile } from './lib/supabase';

// Rutas que requieren autenticación
const protectedRoutes = [
  '/dashboard', 
  '/admin', 
  '/vendor', 
  '/profile', 
  '/become-vendor', 
  '/status'
];

// Rutas específicas que los clientes pueden acceder dentro de vendor
const clientAccessibleVendorRoutes = [
  '/vendor/status',
  '/vendor/application-status', 
  '/vendor/my-application'
];

// Rutas que requieren roles específicos
const roleRoutes: Record<string, string[]> = {
  '/admin': ['administrador', 'admin'],
  '/vendor': ['vendedor', 'administrador', 'admin'],
  '/dashboard': ['cliente', 'vendedor', 'administrador', 'admin'],
  '/become-vendor': ['cliente', 'vendedor', 'administrador', 'admin'],
  '/status': ['cliente', 'vendedor', 'administrador', 'admin'],
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
    
    // **LÓGICA ESPECIAL**: Verificar rutas de vendor accesibles para clientes
    const isClientAccessibleVendorRoute = clientAccessibleVendorRoutes.some(route => 
      pathname.startsWith(route)
    );
    
    if (isClientAccessibleVendorRoute && currentUser.profile?.role === 'cliente') {
      // Permitir acceso a clientes para rutas específicas de vendor
      context.locals.user = currentUser;
      return next();
    }
    
    // **LÓGICA ESPECIAL**: Verificar acceso a rutas de admin
    if (pathname.startsWith('/admin')) {
      const userRole = currentUser.profile?.role?.toLowerCase();
      const userEmail = currentUser.profile?.email?.toLowerCase();
      
      // Lista de emails de admin (deberías tenerla en tu config)
      const adminEmails = [
        'admin@carnaval-oruro.com',
        'soporte.carnaval.oruro@gmail.com'
      ];
      
      const isAdmin = (
        userRole === 'administrador' || 
        userRole === 'admin' ||
        adminEmails.includes(userEmail || '')
      );
      
      if (!isAdmin) {
        // Si no es admin, redirigir según su rol
        switch (userRole) {
          case 'vendedor':
            return redirect('/vendor');
          case 'cliente':
            return redirect('/dashboard');
          default:
            return redirect('/dashboard');
        }
      }
    }
    
    // Verificar roles específicos para otras rutas
    const matchingRoute = Object.keys(roleRoutes).find(route => pathname.startsWith(route));
    const requiredRoles = matchingRoute ? roleRoutes[matchingRoute] : null;
    
    if (requiredRoles && currentUser.profile) {
      const userRole = currentUser.profile.role?.toLowerCase();
      const hasRequiredRole = requiredRoles.some(role => 
        role.toLowerCase() === userRole
      );
      
      if (!hasRequiredRole) {
        // Redirigir según el rol del usuario
        switch (userRole) {
          case 'administrador':
          case 'admin':
            return redirect('/admin/dashboard');
          case 'vendedor':
            return redirect('/vendor');
          case 'cliente':
            return redirect('/dashboard');
          default:
            return redirect('/dashboard');
        }
      }
    }
    
    // Agregar información del usuario al contexto local
    context.locals.user = currentUser;
  }
  
  // Si el usuario ya está autenticado y trata de acceder a login/registro, redirigir al dashboard apropiado
  if ((pathname === '/signin' || pathname === '/signup') && accessToken) {
    const currentUser = await getCurrentUser();
    if (currentUser) {
      const userRole = currentUser.profile?.role?.toLowerCase();
      
      // Redirigir al dashboard apropiado según el rol
      switch (userRole) {
        case 'administrador':
        case 'admin':
          return redirect('/admin/dashboard');
        case 'vendedor':
          return redirect('/vendor');
        case 'cliente':
        default:
          return redirect('/dashboard');
      }
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