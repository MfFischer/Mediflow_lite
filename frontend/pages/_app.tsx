import '../styles/globals.css'
import type { AppProps } from 'next/app'
import { NotificationProvider } from '../contexts/NotificationContext'

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <NotificationProvider>
      <Component {...pageProps} />
    </NotificationProvider>
  )
}
