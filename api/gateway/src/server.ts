import 'dotenv/config';
import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import morgan from 'morgan';
import { createProxyMiddleware } from 'http-proxy-middleware';
import rateLimit from 'express-rate-limit';
import { logger, morganStream } from './middleware/logger';

const app = express();
const PORT = parseInt(process.env.PORT ?? '3001', 10);
const BACKEND_URL = process.env.BACKEND_URL ?? 'http://localhost:8000';
const USSD_URL = process.env.USSD_URL ?? 'http://localhost:8001';

// Security & parsing
app.use(helmet());
app.use(cors({ origin: (process.env.CORS_ORIGINS ?? '*').split(','), credentials: true }));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));
app.use(morgan('combined', { stream: morganStream }));

// Rate limiting
const limiter = rateLimit({
  windowMs: 60_000,
  max: parseInt(process.env.RATE_LIMIT_MAX ?? '120', 10),
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    res.status(429).json({
      error: 'Too Many Requests',
      message: 'Rate limit exceeded. Please slow down.',
      retryAfter: Math.ceil(60),
    });
  },
});
app.use(limiter);

// Health endpoint
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', version: '1.0.0', timestamp: new Date().toISOString(), uptime: process.uptime() });
});

// Proxy: Backend Django API
app.use('/api', createProxyMiddleware({
  target: BACKEND_URL,
  changeOrigin: true,
  on: {
    error: (err, _req, res) => {
      logger.error('Backend proxy error:', err);
      (res as express.Response).status(502).json({ error: 'Bad Gateway', message: 'Backend service unavailable' });
    },
  },
}));

// Proxy: USSD Microservice
app.use('/ussd', createProxyMiddleware({
  target: USSD_URL,
  changeOrigin: true,
  on: {
    error: (err, _req, res) => {
      logger.error('USSD proxy error:', err);
      (res as express.Response).status(502).json({ error: 'Bad Gateway', message: 'USSD service unavailable' });
    },
  },
}));

// 404 handler
app.use((_req, res) => {
  res.status(404).json({ error: 'Not Found', message: 'The requested endpoint does not exist' });
});

// Global error handler
app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  logger.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal Server Error', message: err.message });
});

app.listen(PORT, () => {
  logger.info(`BimaGrid API Gateway running on port ${PORT}`);
  logger.info(`Proxying /api/* -> ${BACKEND_URL}`);
  logger.info(`Proxying /ussd/* -> ${USSD_URL}`);
});

export default app;
