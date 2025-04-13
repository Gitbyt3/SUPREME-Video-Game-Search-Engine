import child_process from 'node:child_process'
import path from 'node:path'

let retrieve: {
    irProcess?: child_process.ChildProcessWithoutNullStreams
} = {
    irProcess: undefined
}
export default retrieve;
export function init() {
    const irPath = path.resolve(process.cwd(), '../MODULES/main.py');
    console.log('calling', 'python', irPath);
    const _irProcess = child_process.spawn('python', ['-u', irPath], {
        cwd: path.resolve(process.cwd(), '..'),
        stdio: ['pipe', 'pipe', 'pipe']
    });
    _irProcess.stdout.on('data', function listener(data) {
      data = data.toString();
      if (data === 'initialized') {
        console.log('IR process initialized');
        _irProcess.stdout.off('data', listener);
        retrieve.irProcess = _irProcess;
      }
      if (!retrieve.irProcess) {
        console.log('Message from IR process:', data);
      }
    });
    _irProcess.stderr.on('data', (data) => {
        console.error(data.toString());
    });
    return _irProcess;
}
