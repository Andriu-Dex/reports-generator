import sys
from analytics import GitHubAnalytics

print("Testing analytics functionality...", flush=True)

# Create test data
test_data = [{
    'Tipo': 'Issue',
    'Estado': 'open',
    'Titulo': 'Test issue',
    'Autor': 'testuser',
    'Fecha_Creacion': '2024-01-01T00:00:00Z'
}]

# Create analytics instance
analytics = GitHubAnalytics(test_data)
print("Analytics instance created successfully", flush=True)

# Test statistics
stats = analytics.obtener_estadisticas_resumen()
print(f"Statistics: {stats['total_items']} items", flush=True)

# Test filtering
filtered = analytics.filter_data(test_data, {'state': 'open'})
print(f"Filtering works: {len(filtered)} items filtered", flush=True)

print("All tests completed successfully!", flush=True)
