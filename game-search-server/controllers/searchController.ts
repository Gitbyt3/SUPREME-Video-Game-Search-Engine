import { Request, Response } from 'express';
import { validateParams } from '../utils/paramValidator';
import retrieveService from '../service/retrieve';
import sqlite3 from 'sqlite3';
import databaseService from '../service/databaseService';

export const handleSearch = (req: Request, res: Response): void => {
  if (!validateParams(req, res, ['keywords'])) return;
  const keywords = req.query.keywords as string;
  if (!retrieveService.irProcess) {
    res.json({
      hasError: true,
      message: 'Server has not initialized...'
    });
    return;
  }
  const reqId = `${Math.random()}`;
  const message = JSON.stringify({
    id: reqId,
    query: keywords
  });
  retrieveService.irProcess.stdin.write(message);
  retrieveService.irProcess.stdin.write('\n');
  console.log('Message sent to IR process', message);

  retrieveService.irProcess.stdout.on('data', function listener(data) {
    console.log('Got message from IR process:', data.toString());
    console.log('Excepting ID:', reqId)
    try {
      data = JSON.parse(data.toString());
      if (data.id === reqId) {
        retrieveService.irProcess?.stdout.off('data', listener);
        // Connect to the SQLite database
        const db = new sqlite3.Database('./games.db', sqlite3.OPEN_READONLY, (err) => {
          if (err) {
            console.error('Error opening database:', err.message);
            res.json({ hasError: true, message: 'Database error' });
            return;
          }
        });

        // Query the database and merge results
        const ids = data.data.map((item: any) => item.ID);
        const placeholders = ids.map(() => '?').join(',');
        const query = `SELECT * FROM games WHERE id IN (${placeholders})`;

        databaseService.query(query, ids)
          .then(rows => {
            // Merge database rows with data.data
            const mergedData = data.data.map((item: any) => {
              const dbRow = rows.find((row: any) => row.id === item.ID);
              if (typeof item === 'object' && item !== null && typeof dbRow === 'object' && dbRow !== null) {
                return { ...item, ...dbRow };
              }
              return item; // Return the original item if merging is not possible
            });
            res.json(mergedData);
          })
          .catch(err => {
            console.error('Error querying database:', err.message);
            res.json({ hasError: true, message: 'Database query error' });
          });
        return;
      }
    } catch(ex) {
      console.error(ex);
      retrieveService.irProcess?.stdout.off('data', listener);
      res.json({hasError: true});
    }
  });
}; 