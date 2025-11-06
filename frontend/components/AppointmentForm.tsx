import React from 'react'

const AppointmentForm = () => {
  return (
    <form>
      <input type="text" placeholder="Patient Name" />
      <input type="date" />
      <button type="submit">Book Appointment</button>
    </form>
  )
}

export default AppointmentForm
