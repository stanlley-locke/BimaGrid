import winston from 'winston';
import { StreamOptions } from 'morgan';

const { combine, timestamp, colorize, printf, json } = winston.format;
const isDev = process.env.NODE_ENV !== 'production';

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL ?? 'info',
  format: isDev
    ? combine(colorize(), timestamp(), printf(({ level, message, timestamp }) => `${timestamp} [${level}]: ${message}`))
    : combine(timestamp(), json()),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'logs/gateway-error.log', level: 'error', maxsize: 52428800, maxFiles: 5 }),
    new winston.transports.File({ filename: 'logs/gateway.log', maxsize: 52428800, maxFiles: 5 }),
  ],
});

export const morganStream: StreamOptions = {
  write: (message: string) => logger.info(message.trim()),
};
