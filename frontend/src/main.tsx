import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { SettingsProvider } from './context/SettingsContext'
import { ThemeProvider } from './context/ThemeContext'
import { ErrorBoundary } from './components/ErrorBoundary'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <SettingsProvider>
        <ErrorBoundary fallbackTitle="ROUTE/IQ Application Recovery">
          <App />
        </ErrorBoundary>
      </SettingsProvider>
    </ThemeProvider>
  </StrictMode>,
)
