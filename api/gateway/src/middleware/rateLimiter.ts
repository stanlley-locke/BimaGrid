import rateLimit from 'express-rate-limit';

export const apiRateLimiter = rateLimit({
  windowMs: 60_000,
  max: parseInt(process.env.RATE_LIMIT_MAX ?? '120', 10),
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => req.ip ?? req.headers['x-forwarded-for']?.toString() ?? 'unknown',
  handler: (_req, res) => {
    res.status(429).json({
      error: 'Too Many Requests',
      message: 'You have exceeded the API rate limit.',
      retryAfter: 60,
    });
  },
});

export const ussdRateLimiter = rateLimit({
  windowMs: 60_000,
  max: 300, // USSD callbacks can be higher volume
  standardHeaders: true,
  legacyHeaders: false,
  handler: (_req, res) => {
    res.status(429).json({ error: 'Too Many Requests', retryAfter: 60 });
  },
});
