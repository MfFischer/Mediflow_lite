import '../styles/globals.css'
import type { AppProps } from 'next/app'
import { NotificationProvider } from '../contexts/NotificationContext'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ToastProvider } from '../contexts/ToastContext'
import ErrorBoundary from '../components/ErrorBoundary'
import { useState } from 'react'

export default function MyApp({ Component, pageProps }: AppProps) {
  // Create QueryClient instance (must be inside component to avoid SSR issues)
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
        retry: 1,
        staleTime: 5 * 60 * 1000, // 5 minutes
      },
    },
  }))

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          <NotificationProvider>
            <Component {...pageProps} />
          </NotificationProvider>
        </ToastProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}
