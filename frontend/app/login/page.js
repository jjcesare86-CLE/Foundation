'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/src/lib/supabase';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) {
      setError(error.message);
      setLoading(false);
    } else {
      router.replace('/os');
    }
  };

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#060816',
      fontFamily: 'DM Sans, sans-serif',
    }}>
      <form onSubmit={handleLogin} style={{
        width: 360,
        padding: 32,
        borderRadius: 12,
        background: '#0d101f',
        border: '1px solid rgba(255,255,255,0.06)',
      }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{
            width: 48, height: 48, borderRadius: 12,
            background: 'linear-gradient(135deg,#6366f1,#8b5cf6)',
            display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: 12,
          }}>
            <svg width={24} height={24} viewBox="0 0 24 24" fill="white"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
          </div>
          <h1 style={{ color: 'white', fontSize: 20, fontFamily: 'Sora, sans-serif', fontWeight: 600, margin: 0 }}>
            Automation Nation
          </h1>
          <p style={{ color: '#545d72', fontSize: 13, marginTop: 4 }}>Sign in to access the AI Employee OS</p>
        </div>

        {error && (
          <div style={{ background: 'rgba(248,113,113,0.1)', border: '1px solid rgba(248,113,113,0.2)', borderRadius: 8, padding: '8px 12px', marginBottom: 16, color: '#f87171', fontSize: 13 }}>
            {error}
          </div>
        )}

        <input
          type="email" placeholder="Email" value={email}
          onChange={(e) => setEmail(e.target.value)} required
          style={inputStyle}
        />
        <input
          type="password" placeholder="Password" value={password}
          onChange={(e) => setPassword(e.target.value)} required
          style={{ ...inputStyle, marginTop: 10 }}
        />
        <button type="submit" disabled={loading} style={{
          width: '100%', marginTop: 16, padding: '10px 0', borderRadius: 8,
          background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', border: 'none',
          color: 'white', fontSize: 14, fontWeight: 600, cursor: 'pointer',
          fontFamily: 'Sora, sans-serif', opacity: loading ? 0.6 : 1,
        }}>
          {loading ? 'Signing in...' : 'Sign In'}
        </button>
      </form>
    </div>
  );
}

const inputStyle = {
  width: '100%',
  padding: '10px 12px',
  borderRadius: 8,
  background: '#080a14',
  border: '1px solid rgba(255,255,255,0.08)',
  color: 'white',
  fontSize: 14,
  fontFamily: 'DM Sans, sans-serif',
  outline: 'none',
  boxSizing: 'border-box',
};
