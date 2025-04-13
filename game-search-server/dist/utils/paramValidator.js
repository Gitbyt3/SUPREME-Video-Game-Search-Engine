"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateParams = void 0;
const validateParams = (req, res, requiredParams) => {
    for (const param of requiredParams) {
        if (!req.query[param]) {
            res.status(400).send(`Error: "${param}" parameter is required.`);
            return false;
        }
    }
    return true;
};
exports.validateParams = validateParams;
