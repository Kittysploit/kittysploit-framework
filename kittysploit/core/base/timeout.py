import signal
import functools


class TimeoutError(Exception):
    pass


def timeout(seconds, error_message="Timeout"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def timeout_handler(signum, frame):
                raise TimeoutError(error_message)

            # Définir le gestionnaire de signal pour SIGALRM
            signal.signal(signal.SIGALRM, timeout_handler)
            # Définir la minuterie d'alarme pour le nombre de secondes spécifié
            signal.alarm(seconds)

            try:
                result = func(*args, **kwargs)
            finally:
                # Réinitialiser la minuterie d'alarme après l'exécution de la fonction
                signal.alarm(0)

            return result

        return wrapper

    return decorator
