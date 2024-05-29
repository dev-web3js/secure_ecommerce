import pytest
from app import create_app, db
from app.models import User, Product

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_register(client):
    response = client.post('/api/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password'
    })
    assert response.status_code == 201

def test_login(client):
    client.post('/api/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password'
    })
    response = client.post('/api/login', json={
        'email': 'test@example.com',
        'password': 'password'
    })
    assert response.status_code == 200
    assert 'access_token' in response.get_json()

def test_get_products(client):
    response = client.get('/api/products')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_get_product(client):
    client.post('/api/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password'
    })
    login_response = client.post('/api/login', json={
        'email': 'test@example.com',
        'password': 'password'
    })
    token = login_response.get_json()['access_token']

    product = Product(name='Sample Product', description='Sample Description', price=10.0, stock=100)
    db.session.add(product)
    db.session.commit()

    response = client.get(f'/api/products/{product.id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    product_data = response.get_json()
    assert product_data['name'] == 'Sample Product'