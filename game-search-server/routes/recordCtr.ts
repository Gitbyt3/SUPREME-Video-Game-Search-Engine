import { Router } from 'express';
import { handleRecordCtr } from '../controllers/recordCtrController';

const router = Router();

router.get('/', handleRecordCtr);

export default router; 