"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleRecordCtr = void 0;
const paramValidator_1 = require("../utils/paramValidator");
const databaseService_1 = __importDefault(require("../service/databaseService"));
const handleRecordCtr = (req, res) => {
    if (!(0, paramValidator_1.validateParams)(req, res, ['id']))
        return;
    const id = +req.query.id;
    if (isNaN(id)) {
        res.end();
        return;
    }
    const sql = `UPDATE games SET ctr = ctr + 1 WHERE id = ?`;
    databaseService_1.default.update(sql, [id])
        .then(() => {
        res.json({ success: true, message: 'CTR updated successfully.' });
    })
        .catch(err => {
        console.error('Error updating CTR:', err.message);
        res.json({ hasError: true, message: 'Database update error' });
    });
};
exports.handleRecordCtr = handleRecordCtr;
