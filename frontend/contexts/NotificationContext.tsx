import { createContext, useContext, useState, ReactNode } from 'react'
import NotificationToast, { Notification } from '../components/NotificationToast'

interface NotificationContextType {
  showNotification: (notification: Omit<Notification, 'id'>) => void
  showSuccess: (title: string, message: string) => void
  showError: (title: string, message: string) => void
  showWarning: (title: string, message: string) => void
  showInfo: (title: string, message: string) => void
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined)

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([])

  const showNotification = (notification: Omit<Notification, 'id'>) => {
    const id = Math.random().toString(36).substring(7)
    setNotifications((prev) => [...prev, { ...notification, id }])
  }

  const showSuccess = (title: string, message: string) => {
    showNotification({ type: 'success', title, message })
  }

  const showError = (title: string, message: string) => {
    showNotification({ type: 'error', title, message })
  }

  const showWarning = (title: string, message: string) => {
    showNotification({ type: 'warning', title, message })
  }

  const showInfo = (title: string, message: string) => {
    showNotification({ type: 'info', title, message })
  }

  const removeNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }

  return (
    <NotificationContext.Provider
      value={{ showNotification, showSuccess, showError, showWarning, showInfo }}
    >
      {children}
      <NotificationToast notifications={notifications} onRemove={removeNotification} />
    </NotificationContext.Provider>
  )
}

export function useNotification() {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotification must be used within NotificationProvider')
  }
  return context
}

