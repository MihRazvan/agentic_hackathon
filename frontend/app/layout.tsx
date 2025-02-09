import '@coinbase/onchainkit/styles.css';
import type { Metadata } from 'next';
import './globals.css';
import { Providers } from './providers';
import { Cinzel } from 'next/font/google';
import { Navigation } from './components/Navigation';

const cinzel = Cinzel({
  subsets: ['latin'],
  variable: '--font-cinzel',
});

export const metadata: Metadata = {
  title: 'Tabula - The DAO Intelligence Hub',
  description: 'Transmute data into decisions',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={cinzel.variable}>
      <body>
        <Providers>
          <Navigation />
          {children}
        </Providers>
      </body>
    </html>
  );
}