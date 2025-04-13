import { Router } from 'express';
import { handleSearch } from '../controllers/searchController';

const router = Router();

router.get('/', handleSearch);

export default router; 