import { AxiosError } from 'axios'

export interface ErrorResponse {
  message: string
  code?: string
  field?: string
  details?: any
}

export class AppError extends Error {
  code: string
  statusCode: number
  isOperational: boolean

  constructor(message: string, code: string = 'UNKNOWN_ERROR', statusCode: number = 500) {
    super(message)
    this.code = code
    this.statusCode = statusCode
    this.isOperational = true
    Object.setPrototypeOf(this, AppError.prototype)
  }
}

/**
 * Parse error from API response
 */
export function parseApiError(error: unknown): ErrorResponse {
  if (error instanceof AxiosError) {
    const response = error.response

    // Handle specific HTTP status codes
    if (response?.status === 401) {
      return {
        message: 'Your session has expired. Please login again.',
        code: 'UNAUTHORIZED',
      }
    }

    if (response?.status === 403) {
      return {
        message: 'You do not have permission to perform this action.',
        code: 'FORBIDDEN',
      }
    }

    if (response?.status === 404) {
      return {
        message: 'The requested resource was not found.',
        code: 'NOT_FOUND',
      }
    }

    if (response?.status === 422) {
      // Validation error
      const detail = response.data?.detail
      if (Array.isArray(detail)) {
        const firstError = detail[0]
        return {
          message: firstError.msg || 'Validation error',
          code: 'VALIDATION_ERROR',
          field: firstError.loc?.[1],
          details: detail,
        }
      }
      return {
        message: detail || 'Validation error',
        code: 'VALIDATION_ERROR',
      }
    }

    if (response?.status === 429) {
      return {
        message: 'Too many requests. Please try again later.',
        code: 'RATE_LIMIT_EXCEEDED',
      }
    }

    if (response?.status >= 500) {
      return {
        message: 'A server error occurred. Please try again later.',
        code: 'SERVER_ERROR',
      }
    }

    // Generic API error
    return {
      message: response?.data?.detail || error.message || 'An error occurred',
      code: 'API_ERROR',
    }
  }

  if (error instanceof AppError) {
    return {
      message: error.message,
      code: error.code,
    }
  }

  if (error instanceof Error) {
    return {
      message: error.message,
      code: 'UNKNOWN_ERROR',
    }
  }

  return {
    message: 'An unexpected error occurred',
    code: 'UNKNOWN_ERROR',
  }
}

/**
 * Display user-friendly error message
 */
export function getUserFriendlyMessage(error: unknown): string {
  const parsed = parseApiError(error)
  return parsed.message
}

/**
 * Check if error is a network error
 */
export function isNetworkError(error: unknown): boolean {
  if (error instanceof AxiosError) {
    return !error.response && error.code === 'ERR_NETWORK'
  }
  return false
}

/**
 * Check if error requires re-authentication
 */
export function requiresReauth(error: unknown): boolean {
  if (error instanceof AxiosError) {
    return error.response?.status === 401
  }
  return false
}

/**
 * Retry logic for failed requests
 */
export async function retryRequest<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  let lastError: unknown

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error

      // Don't retry on client errors (4xx)
      if (error instanceof AxiosError && error.response?.status && error.response.status < 500) {
        throw error
      }

      // Wait before retrying (exponential backoff)
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
      }
    }
  }

  throw lastError
}

/**
 * Log error to monitoring service
 */
export function logError(error: unknown, context?: Record<string, any>) {
  const parsed = parseApiError(error)

  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.error('Error:', parsed, context)
  }

  // TODO: Send to error tracking service (Sentry, LogRocket, etc.)
  // if (typeof window !== 'undefined' && window.Sentry) {
  //   window.Sentry.captureException(error, {
  //     extra: { ...context, parsed },
  //   })
  // }
}

