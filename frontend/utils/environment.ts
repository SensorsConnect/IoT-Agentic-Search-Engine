declare const process: {
  env: {
    NEXT_PUBLIC_BACKEND_URL?: string;
  };
};

const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL ?? '';

export const config = {
  apiUrl: apiUrl
} 