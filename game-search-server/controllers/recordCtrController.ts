import { Request, Response } from 'express';
import { validateParams } from '../utils/paramValidator';
import databaseService from '../service/databaseService';
import retrieveService from '../service/retrieve';

export const handleRecordCtr = (req: Request, res: Response): void => {
  if (!validateParams(req, res, ['id'])) return;
  const id = +(req.query.id as string);
  if (isNaN(id)) {
    res.end();
    return;
  }
  const sql = `UPDATE games SET ctr = ctr + 1 WHERE id = ?`;
  databaseService.update(sql, [id])
    .then(() => {
      res.json({ success: true, message: 'CTR updated successfully.' });
    })
    .catch(err => {
      console.error('Error updating CTR:', err.message);
      res.json({ hasError: true, message: 'Database update error' });
    });
}; 
