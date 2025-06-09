import { render, screen } from '@testing-library/react';
import App from './App';

test('shows login button', () => {
  render(<App />);
  const loginButton = screen.getByRole('button', { name: /login/i });
  expect(loginButton).toBeInTheDocument();
});
