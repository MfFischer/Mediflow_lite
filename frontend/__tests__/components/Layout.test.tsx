import { render, screen, fireEvent } from '@testing-library/react'
import Layout from '../../components/Layout'
import { useRouter } from 'next/router'
import * as auth from '../../utils/auth'

jest.mock('next/router', () => ({
  useRouter: jest.fn(),
}))

jest.mock('../../utils/auth')

describe('Layout Component', () => {
  const mockPush = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
      pathname: '/dashboard',
    })
  })

  it('should render children', () => {
    ;(auth.getCurrentUser as jest.Mock).mockReturnValue({
      id: 1,
      username: 'testuser',
      role: 'doctor',
    })

    render(
      <Layout>
        <div>Test Content</div>
      </Layout>
    )

    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  it('should display user information', () => {
    ;(auth.getCurrentUser as jest.Mock).mockReturnValue({
      id: 1,
      username: 'Dr. Smith',
      role: 'doctor',
    })

    render(
      <Layout>
        <div>Content</div>
      </Layout>
    )

    expect(screen.getByText(/Dr. Smith/i)).toBeInTheDocument()
  })

  it('should handle logout', () => {
    ;(auth.getCurrentUser as jest.Mock).mockReturnValue({
      id: 1,
      username: 'testuser',
      role: 'doctor',
    })

    render(
      <Layout>
        <div>Content</div>
      </Layout>
    )

    const logoutButton = screen.getByText(/logout/i)
    fireEvent.click(logoutButton)

    expect(auth.logout).toHaveBeenCalled()
    expect(mockPush).toHaveBeenCalledWith('/login')
  })
})

