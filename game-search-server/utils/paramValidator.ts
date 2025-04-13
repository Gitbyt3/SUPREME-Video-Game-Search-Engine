import { Request, Response } from 'express';

export const validateParams = (req: Request, res: Response, requiredParams: string[]): boolean => {
  for (const param of requiredParams) {
    if (!req.query[param]) {
      res.status(400).send(`Error: "${param}" parameter is required.`);
      return false;
    }
  }
  return true;
}; 