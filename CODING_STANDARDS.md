# Estándares de Código y Mejores Prácticas

## 1. Principios Fundamentales

### 1.1 SOLID
Todos los desarrolladores deben aplicar los principios SOLID:

#### Single Responsibility Principle (SRP)
```python
# ❌ MAL - Múltiples responsabilidades
class UserManager:
    def create_user(self, data): ...
    def send_email(self, user): ...
    def save_to_db(self, user): ...
    def validate_password(self, password): ...

# ✅ BIEN - Responsabilidades separadas
class UserCreator:
    def create(self, data): ...

class EmailService:
    def send_welcome_email(self, user): ...

class UserRepository:
    def save(self, user): ...

class PasswordValidator:
    def validate(self, password): ...
```

#### Open/Closed Principle (OCP)
```python
# ❌ MAL - Modificar clase existente para nueva funcionalidad
class ReportGenerator:
    def generate_pdf(self, data): ...
    # Se añade después:
    def generate_excel(self, data): ...

# ✅ BIEN - Extender sin modificar
class ReportGenerator:
    def generate(self, data, formatter): ...

class PDFFormatter:
    def format(self, data): ...

class ExcelFormatter:
    def format(self, data): ...
```

#### Liskov Substitution Principle (LSP)
```python
# ❌ MAL - Subtipo cambia comportamiento
class Bird:
    def fly(self): ...

class Penguin(Bird):  # Los pingüinos no vuelan
    def fly(self):
        raise NotImplementedError

# ✅ BIEN - Jerarquía correcta
class Bird:
    pass

class FlyingBird(Bird):
    def fly(self): ...

class NonFlyingBird(Bird):
    pass

class Eagle(FlyingBird): ...
class Penguin(NonFlyingBird): ...
```

#### Interface Segregation Principle (ISP)
```python
# ❌ MAL - Interfaz monolítica
class Worker:
    def work(self): ...
    def eat(self): ...
    def sleep(self): ...

# ✅ BIEN - Interfaces específicas
class Workable:
    def work(self): ...

class Eatable:
    def eat(self): ...

class Sleepable:
    def sleep(self): ...
```

#### Dependency Inversion Principle (DIP)
```python
# ❌ MAL - Dependencia concreta
class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # Dependencia concreta

# ✅ BIEN - Dependencia de abstracción
class UserService:
    def __init__(self, database: DatabaseInterface):
        self.db = database
```

### 1.2 DRY (Don't Repeat Yourself)
- Extraer lógica duplicada a funciones/métodos
- Crear utilidades compartidas
- Usar herencia/composición para compartir comportamiento

```python
# ❌ MAL - Código duplicado
def calculate_order_total(order):
    total = 0
    for item in order.items:
        total += item.price * item.quantity
    total += total * 0.21  # IVA
    
def calculate_invoice_total(invoice):
    total = 0
    for item in invoice.items:
        total += item.price * item.quantity
    total += total * 0.21  # IVA

# ✅ BIEN - Código reutilizado
def calculate_subtotal(items):
    return sum(item.price * item.quantity for item in items)

def apply_tax(amount, tax_rate=0.21):
    return amount + (amount * tax_rate)

def calculate_order_total(order):
    subtotal = calculate_subtotal(order.items)
    return apply_tax(subtotal)

def calculate_invoice_total(invoice):
    subtotal = calculate_subtotal(invoice.items)
    return apply_tax(subtotal)
```

## 2. Estándares de Código Python

### 2.1 Estilo y Formato
- Seguir PEP 8
- Límite de 79 caracteres por línea
- 4 espacios por indentación (no tabs)
- Nombres en snake_case para funciones/variables
- Nombres en PascalCase para clases

### 2.2 Tipado
- Usar type hints en todas las funciones y métodos
- Validar con mypy en CI/CD

```python
# ✅ BIEN - Type hints completos
from typing import List, Optional, Dict

def process_users(users: List[User]) -> Dict[str, int]:
    """Procesa lista de usuarios y retorna estadísticas."""
    # Implementación
    return {"total": len(users)}

class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository
    
    def get_user(self, user_id: int) -> Optional[User]:
        return self.repository.find_by_id(user_id)
```

### 2.3 Documentación
- Docstrings en formato Google Style
- Documentar parámetros, retorno y excepciones
- Comentarios solo para lógica compleja

```python
def calculate_discount(price: float, customer_type: str) -> float:
    """Calcula el descuento aplicable a un precio.
    
    Args:
        price: Precio original del producto
        customer_type: Tipo de cliente ('regular', 'premium', 'vip')
    
    Returns:
        Precio con descuento aplicado
    
    Raises:
        ValueError: Si customer_type no es válido
    """
    if customer_type not in DISCOUNT_RATES:
        raise ValueError(f"Tipo de cliente inválido: {customer_type}")
    
    discount_rate = DISCOUNT_RATES[customer_type]
    return price * (1 - discount_rate)
```

## 3. Patrones de Diseño Recomendados

### 3.1 Repository Pattern
```python
# Interfaz de repositorio
class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    def save(self, user: User) -> User:
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass

# Implementación concreta
class SQLUserRepository(UserRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        return self.session.query(User).get(user_id)
```

### 3.2 Service Pattern
```python
class UserService:
    def __init__(self, repository: UserRepository, email_service: EmailService):
        self.repository = repository
        self.email_service = email_service
    
    def register_user(self, user_data: Dict) -> User:
        # Lógica de negocio centralizada
        user = User(**user_data)
        self.repository.save(user)
        self.email_service.send_welcome_email(user)
        return user
```

### 3.3 Dependency Injection
```python
# Container de dependencias
class Container:
    def __init__(self):
        self.db_session = create_session()
        self.email_service = EmailService()
    
    def user_repository(self) -> UserRepository:
        return SQLUserRepository(self.db_session)
    
    def user_service(self) -> UserService:
        return UserService(
            repository=self.user_repository(),
            email_service=self.email_service
        )

# Uso
container = Container()
user_service = container.user_service()
```

## 4. Testing

### 4.1 Estructura de Tests
```
tests/
├── unit/
│   ├── services/
│   ├── repositories/
│   └── utils/
├── integration/
│   ├── api/
│   └── database/
└── e2e/
```

### 4.2 Convenciones de Nombres
```python
# test_<module>_<functionality>.py
test_user_service_register.py
test_user_repository_find_by_id.py

# Métodos de test: test_<scenario>_<expected_behavior>
def test_register_user_with_valid_data_returns_user():
    pass

def test_register_user_with_existing_email_raises_error():
    pass
```

### 4.3 Fixtures y Mocks
```python
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_repository():
    return Mock(spec=UserRepository)

@pytest.fixture
def user_service(mock_repository):
    return UserService(repository=mock_repository)

def test_get_user_returns_user(user_service, mock_repository):
    expected_user = User(id=1, name="Test")
    mock_repository.find_by_id.return_value = expected_user
    
    result = user_service.get_user(1)
    
    assert result == expected_user
    mock_repository.find_by_id.assert_called_once_with(1)
```

## 5. Configuración y Entorno

### 5.1 Variables de Entorno
```python
# config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_key: str
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 5.2 Logging
```python
import logging
import structlog

# Configuración estructurada
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
```

## 6. Code Review Checklist

### 6.1 Checklist Obligatorio
- [ ] ¿Cumple con principios SOLID?
- [ ] ¿Hay código duplicado (viola DRY)?
- [ ] ¿Tiene type hints completos?
- [ ] ¿Tiene docstrings adecuados?
- [ ] ¿Sigue PEP 8?
- [ ] ¿Tiene tests unitarios?
- [ ] ¿Cobertura de tests > 80%?
- [ ] ¿Maneja errores adecuadamente?
- [ ] ¿Es seguro (no tiene vulnerabilidades)?
- [ ] ¿Es performante?

### 6.2 Puntos de Atención Especial
- **Inyección de dependencias:** ¿Usa DI en lugar de instanciación directa?
- **Acoplamiento:** ¿Está desacoplado de implementaciones concretas?
- **Cohesión:** ¿Cada clase tiene una responsabilidad clara?
- **Testabilidad:** ¿Es fácil de testear en aislamiento?
- **Mantenibilidad:** ¿Es fácil de entender y modificar?

## 7. Herramientas de Calidad

### 7.1 Automatización
```yaml
# .github/workflows/quality.yml
name: Quality Checks
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      
      - name: Run black (formatter)
        run: black --check .
      
      - name: Run isort (imports)
        run: isort --check-only .
      
      - name: Run flake8 (linting)
        run: flake8 .
      
      - name: Run mypy (type checking)
        run: mypy .
      
      - name: Run pytest with coverage
        run: pytest --cov=. --cov-report=xml
      
      - name: Check coverage
        run: |
          coverage report --fail-under=80
```

### 7.2 Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/PyCQA/isort
    rev: 5.10.1
    hooks:
      - id: isort
  
  - repo: https://github.com/PyCQA/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

---

**Última actualización:** 2026-04-08  
**Responsable de mantener:** Main Developer  
**Aprobado por:** Arquitecto