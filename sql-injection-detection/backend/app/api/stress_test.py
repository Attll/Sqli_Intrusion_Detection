from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.auth import verify_api_key
from app.schemas.request import StressTestRequest
from app.services.detection_service import DetectionService
from app.utils.payload_generator import PayloadGenerator
from typing import Dict, Any
import uuid
import time

router = APIRouter()

# In-memory store for test statuses/results
STRESS_TESTS: Dict[str, Dict[str, Any]] = {}


def _create_db_session():
    return SessionLocal()


def _run_stress_test(test_id: str, request: StressTestRequest):
    """Background worker that runs the stress test and stores results."""
    try:
        db = _create_db_session()
        service = DetectionService(db)
        generator = PayloadGenerator()

        # Determine ratios
        if request.include_benign:
            malicious_ratio = 0.7
        else:
            malicious_ratio = 1.0

        total = request.num_requests
        payloads = generator.generate_mixed_payloads(total, malicious_ratio)

        # Metrics
        tp = fp = tn = fn = 0
        total_time_ms = 0.0

        start_time = time.time()
        for i, p in enumerate(payloads):
            q = p['query']
            is_malicious_actual = p['is_malicious']

            try:
                res = service.detect(query=q, endpoint='/stress-test', use_ensemble=False)
                is_malicious_pred = res.get('is_malicious', False)
                proc_ms = res.get('processing_time_ms', 0.0)

                total_time_ms += proc_ms

                if is_malicious_actual and is_malicious_pred:
                    tp += 1
                elif not is_malicious_actual and is_malicious_pred:
                    fp += 1
                elif not is_malicious_actual and not is_malicious_pred:
                    tn += 1
                elif is_malicious_actual and not is_malicious_pred:
                    fn += 1

                # Update progress periodically
                if (i + 1) % 50 == 0 or (i + 1) == total:
                    STRESS_TESTS[test_id]['progress'] = (i + 1) / total

            except Exception as e:
                # Count as failed prediction
                STRESS_TESTS[test_id]['errors'].append(str(e))

        end_time = time.time()
        duration = end_time - start_time
        requests_per_sec = total / max(duration, 1e-6)

        accuracy = (tp + tn) / max(total, 1)
        avg_processing_ms = total_time_ms / max(total, 1)

        results = {
            'total_requests': total,
            'true_positives': tp,
            'false_positives': fp,
            'true_negatives': tn,
            'false_negatives': fn,
            'accuracy': accuracy,
            'avg_processing_time_ms': avg_processing_ms,
            'requests_per_second': requests_per_sec
        }

        STRESS_TESTS[test_id]['status'] = 'completed'
        STRESS_TESTS[test_id]['results'] = results

    except Exception as e:
        STRESS_TESTS[test_id]['status'] = 'failed'
        STRESS_TESTS[test_id]['errors'].append(str(e))
    finally:
        try:
            db.close()
        except:
            pass


@router.post('/generate-payloads')
async def generate_payloads(request: StressTestRequest, api_key=Depends(verify_api_key)):
    """Generate payloads for stress testing."""
    try:
        gen = PayloadGenerator()
        malicious_ratio = 0.7 if request.include_benign else 1.0
        payloads = gen.generate_mixed_payloads(request.num_requests, malicious_ratio)
        return {'count': len(payloads), 'payloads': payloads}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/run')
async def run_stress_test(request: StressTestRequest, background_tasks: BackgroundTasks, api_key=Depends(verify_api_key)):
    """Start a stress test in the background and return a test id."""
    try:
        test_id = uuid.uuid4().hex
        STRESS_TESTS[test_id] = {
            'status': 'running',
            'progress': 0.0,
            'results': None,
            'errors': []
        }

        # Schedule background worker
        background_tasks.add_task(_run_stress_test, test_id, request)

        return {'test_id': test_id, 'status': 'started'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/status/{test_id}')
async def get_status(test_id: str, api_key=Depends(verify_api_key)):
    """Get status and results for a stress test."""
    test = STRESS_TESTS.get(test_id)
    if not test:
        raise HTTPException(status_code=404, detail='Test ID not found')

    return {
        'test_id': test_id,
        'status': test['status'],
        'progress': test.get('progress', 0.0),
        'results': test.get('results'),
        'errors': test.get('errors', [])
    }
