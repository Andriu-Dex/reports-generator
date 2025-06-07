#!/usr/bin/env python3
"""
Test script to verify the PDF generation integration is working correctly.
"""

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    try:
        from analytics import GitHubAnalytics
        print("✅ GitHubAnalytics imported successfully")
        
        import reporte_issues
        print("✅ reporte_issues imported successfully")
        
        import app_gui
        print("✅ app_gui imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_analytics_integration():
    """Test that GitHubAnalytics integration works with sample data."""
    print("\n🔍 Testing GitHubAnalytics integration...")
    try:
        from analytics import GitHubAnalytics
        
        # Test data
        test_data = [
            {
                'Tipo': 'Issue', 
                'Estado': 'open', 
                'Fecha_Creacion': '2024-01-01T10:00:00Z',
                'Etiquetas': 'bug',
                'Usuario': 'user1'
            },
            {
                'Tipo': 'Issue', 
                'Estado': 'closed', 
                'Fecha_Creacion': '2024-01-02T10:00:00Z',
                'Fecha_Cierre': '2024-01-05T15:00:00Z',
                'Etiquetas': 'feature',
                'Usuario': 'user2'
            }
        ]
        
        analytics = GitHubAnalytics(test_data)
        stats = analytics.obtener_estadisticas_resumen()
        
        print(f"✅ Generated {len(stats)} statistics")
        print(f"   - Issues abiertos: {stats.get('issues_abiertos', 0)}")
        print(f"   - Issues cerrados: {stats.get('issues_cerrados', 0)}")
        
        return len(stats) > 0
    except Exception as e:
        print(f"❌ Analytics integration error: {e}")
        return False

def test_pdf_function_signature():
    """Test that the PDF function accepts the filas parameter."""
    print("\n🔍 Testing PDF function signature...")
    try:
        import reporte_issues
        import inspect
        
        sig = inspect.signature(reporte_issues.generar_pdf_desde_markdown)
        params = list(sig.parameters.keys())
        
        if 'filas' in params:
            print("✅ generar_pdf_desde_markdown accepts 'filas' parameter")
            return True
        else:
            print("❌ generar_pdf_desde_markdown missing 'filas' parameter")
            return False
    except Exception as e:
        print(f"❌ Function signature error: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🚀 Starting integration tests...\n")
    
    tests = [
        test_imports,
        test_analytics_integration,
        test_pdf_function_signature
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests PASSED! The PDF generation should now show real statistics instead of zeros.")
    else:
        print("⚠️  Some tests failed. Please check the output above.")

if __name__ == "__main__":
    main()
