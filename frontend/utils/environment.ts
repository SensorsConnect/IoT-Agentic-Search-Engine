declare const process: {
  env: {
    NEXT_PUBLIC_BACKEND_URL?: string;
  };
};

const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL ?? '';
console.log('Environment config:', {
  NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL,
  apiUrl: apiUrl
});

export const config = {
  apiUrl: apiUrl
} 