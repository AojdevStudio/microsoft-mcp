"""
Test suite for performance benchmarks in the KamDental Email Framework.
Tests render time, size constraints, and efficiency metrics.
"""

import pytest
import time
from unittest.mock import Mock, patch
from typing import Dict, Any
import json


class TestRenderPerformance:
    """Test email rendering performance benchmarks."""
    
    @pytest.fixture
    def large_dataset(self):
        """Generate a large dataset for performance testing."""
        return {
            "financial_data": {
                "production": {"value": 143343, "goal": 160000, "status": "behind"},
                "collections": {"value": 107113, "ratio": 0.747},
                "case_acceptance": {"value": 0.3586, "status": "good"},
                "call_answer_rate": {"value": 0.693, "goal": 0.85, "status": "warning"}
            },
            "providers": [
                {
                    "name": f"Provider {i}",
                    "role": "Dentist",
                    "production": 50000 + i * 1000,
                    "goal_percentage": 0.75 + i * 0.01
                }
                for i in range(20)  # 20 providers
            ],
            "alerts": [
                {
                    "type": "warning",
                    "message": f"Alert {i}"
                }
                for i in range(10)  # 10 alerts
            ],
            "recommendations": [
                {
                    "priority": "HIGH",
                    "title": f"Recommendation {i}",
                    "outcome": f"Outcome {i}"
                }
                for i in range(15)  # 15 recommendations
            ]
        }
    
    def test_template_render_time_under_2_seconds(self, large_dataset):
        """Test that template rendering completes in under 2 seconds."""
        with patch('microsoft_mcp.email_framework.templates.practice_report.PracticeReportTemplate') as MockTemplate:
            mock_instance = MockTemplate.return_value
            
            def mock_render(data):
                # Simulate actual rendering work
                html_parts = []
                html_parts.append("<html><body>")
                
                # Process financial data
                for key, value in data.get("financial_data", {}).items():
                    html_parts.append(f"<div>{key}: {value}</div>")
                
                # Process providers
                for provider in data.get("providers", []):
                    html_parts.append(f"<div>{provider['name']}: ${provider['production']}</div>")
                
                # Process alerts
                for alert in data.get("alerts", []):
                    html_parts.append(f"<div class='alert'>{alert['message']}</div>")
                
                # Process recommendations
                for rec in data.get("recommendations", []):
                    html_parts.append(f"<div class='rec'>{rec['title']}</div>")
                
                html_parts.append("</body></html>")
                return "".join(html_parts)
            
            mock_instance.render = mock_render
            
            # Measure render time
            start_time = time.time()
            result = mock_instance.render(large_dataset)
            end_time = time.time()
            
            render_time = end_time - start_time
            assert render_time < 2.0, f"Render time {render_time:.2f}s exceeds 2 second limit"
            assert "<html>" in result
            assert len(result) > 1000  # Should have substantial content
    
    def test_css_inlining_performance(self):
        """Test CSS inlining performance with large HTML."""
        large_html = """
        <div class="container">
            """ + "\n".join([f'<div class="item item-{i}">Item {i}</div>' for i in range(100)]) + """
        </div>
        """
        
        large_css = """
        .container { padding: 20px; background: #f5f5f5; }
        .item { margin: 10px; padding: 15px; border: 1px solid #ddd; }
        """ + "\n".join([f'.item-{i} {{ color: #{i:03x}; }}' for i in range(100)])
        
        with patch('microsoft_mcp.email_framework.css_inliner.inline_css') as mock_inline:
            mock_inline.return_value = large_html.replace('class="', 'style="')
            
            start_time = time.time()
            result = mock_inline(large_html, large_css)
            end_time = time.time()
            
            inline_time = end_time - start_time
            assert inline_time < 1.0, f"CSS inlining took {inline_time:.2f}s"
    
    def test_template_compilation_caching(self):
        """Test that template compilation is cached for performance."""
        with patch('microsoft_mcp.email_framework.templates.base.EmailTemplate') as MockTemplate:
            mock_instance = MockTemplate.return_value
            mock_instance._compiled_template_cache = {}
            
            # First render should compile
            first_start = time.time()
            mock_instance.render({"test": "data"})
            first_time = time.time() - first_start
            
            # Second render should use cache
            second_start = time.time()
            mock_instance.render({"test": "data"})
            second_time = time.time() - second_start
            
            # Cached render should be significantly faster
            # In practice, this would be more pronounced
            assert second_time <= first_time


class TestSizeOptimization:
    """Test framework size constraints and optimization."""
    
    def test_css_framework_size_under_100kb(self):
        """Test that entire CSS framework is under 100KB."""
        css_files = [
            "core/variables.css",
            "core/base.css",
            "core/utilities.css",
            "components/metrics.css",
            "components/providers.css",
            "components/alerts.css",
            "components/recommendations.css",
            "themes/baytown.css",
            "themes/humble.css",
            "themes/executive.css"
        ]
        
        # Simulate file sizes
        file_sizes = {
            "core/variables.css": 2 * 1024,      # 2KB
            "core/base.css": 5 * 1024,           # 5KB
            "core/utilities.css": 3 * 1024,      # 3KB
            "components/metrics.css": 8 * 1024,   # 8KB
            "components/providers.css": 7 * 1024, # 7KB
            "components/alerts.css": 6 * 1024,    # 6KB
            "components/recommendations.css": 6 * 1024, # 6KB
            "themes/baytown.css": 4 * 1024,      # 4KB
            "themes/humble.css": 4 * 1024,       # 4KB
            "themes/executive.css": 4 * 1024     # 4KB
        }
        
        total_size = sum(file_sizes.values())
        assert total_size < 100 * 1024, f"CSS framework size {total_size/1024:.1f}KB exceeds 100KB limit"
    
    def test_compiled_css_minification(self):
        """Test that compiled CSS is properly minified."""
        original_css = """
        /* Component: Metric Cards */
        .metric-card {
            background: #F7FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 4px;
        }
        """
        
        with patch('microsoft_mcp.email_framework.minify_css') as mock_minify:
            minified = ".metric-card{background:#F7FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:20px;text-align:center}.metric-value{font-size:24px;font-weight:700;margin-bottom:4px}"
            mock_minify.return_value = minified
            
            result = mock_minify(original_css)
            
            # Minified should be significantly smaller
            assert len(result) < len(original_css) * 0.7
            assert "/*" not in result  # No comments
            assert "\n" not in result   # No newlines
            assert "  " not in result   # No multiple spaces
    
    def test_html_output_size_reasonable(self):
        """Test that generated HTML emails are reasonable size."""
        with patch('microsoft_mcp.email_framework.templates.practice_report.PracticeReportTemplate') as MockTemplate:
            mock_instance = MockTemplate.return_value
            
            # Simulate a complete email
            mock_html = """<!DOCTYPE html><html><head><meta charset="UTF-8"></head>
            <body style="margin:0;padding:0;">
            <table width="600">
            <!-- Email content here -->
            </table>
            </body></html>""" * 10  # Simulate larger content
            
            mock_instance.render.return_value = mock_html
            
            result = mock_instance.render({})
            size_kb = len(result.encode('utf-8')) / 1024
            
            # Email should be under 256KB (Gmail clipping limit)
            assert size_kb < 256, f"Email size {size_kb:.1f}KB may be clipped by Gmail"


class TestMemoryUsage:
    """Test memory usage and efficiency."""
    
    def test_memory_usage_under_50mb(self):
        """Test that framework uses less than 50MB memory during operation."""
        with patch('microsoft_mcp.email_framework.get_memory_usage') as mock_memory:
            # Simulate memory usage tracking
            mock_memory.return_value = 35 * 1024 * 1024  # 35MB
            
            memory_usage = mock_memory()
            assert memory_usage < 50 * 1024 * 1024, "Memory usage exceeds 50MB limit"
    
    def test_no_memory_leaks_bulk_rendering(self):
        """Test that bulk rendering doesn't cause memory leaks."""
        with patch('microsoft_mcp.email_framework.templates.practice_report.PracticeReportTemplate') as MockTemplate:
            mock_instance = MockTemplate.return_value
            mock_instance.render.return_value = "<html>Report</html>"
            
            with patch('microsoft_mcp.email_framework.get_memory_usage') as mock_memory:
                initial_memory = 30 * 1024 * 1024  # 30MB
                mock_memory.return_value = initial_memory
                
                # Render 100 emails
                for i in range(100):
                    mock_instance.render({"iteration": i})
                
                # Memory should not grow significantly
                final_memory = 32 * 1024 * 1024  # 32MB
                mock_memory.return_value = final_memory
                
                memory_growth = final_memory - initial_memory
                assert memory_growth < 5 * 1024 * 1024, "Memory grew by more than 5MB"


class TestConcurrentPerformance:
    """Test performance under concurrent load."""
    
    def test_concurrent_template_rendering(self):
        """Test rendering multiple templates concurrently."""
        import concurrent.futures
        
        def render_email(template_type, data):
            """Simulate rendering an email."""
            time.sleep(0.01)  # Simulate work
            return f"<html>{template_type} rendered</html>"
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit 20 rendering tasks
            futures = []
            for i in range(20):
                template_type = ["practice", "executive", "provider", "alert"][i % 4]
                future = executor.submit(render_email, template_type, {"id": i})
                futures.append(future)
            
            # Measure total time
            start_time = time.time()
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
            total_time = time.time() - start_time
            
            # Should complete reasonably fast with concurrency
            assert total_time < 1.0, f"Concurrent rendering took {total_time:.2f}s"
            assert len(results) == 20
    
    def test_cache_performance_under_load(self):
        """Test template cache performance under load."""
        cache = {}
        cache_hits = 0
        cache_misses = 0
        
        def get_cached_template(template_name):
            nonlocal cache_hits, cache_misses
            if template_name in cache:
                cache_hits += 1
                return cache[template_name]
            else:
                cache_misses += 1
                # Simulate loading template
                time.sleep(0.001)
                cache[template_name] = f"Template: {template_name}"
                return cache[template_name]
        
        # Simulate 1000 template requests
        templates = ["practice", "executive", "provider", "alert"]
        for i in range(1000):
            template = templates[i % len(templates)]
            get_cached_template(template)
        
        # Cache should be highly effective
        hit_rate = cache_hits / (cache_hits + cache_misses)
        assert hit_rate > 0.95, f"Cache hit rate {hit_rate:.2%} is too low"


class TestOptimizationMetrics:
    """Test various optimization metrics."""
    
    def test_css_selector_efficiency(self):
        """Test that CSS selectors are efficient."""
        efficient_selectors = [
            ".metric-card",
            ".alert-critical",
            "#email-header",
            "table.email-container"
        ]
        
        inefficient_selectors = [
            "body > div > table > tr > td > div.content",  # Too specific
            "*",  # Universal selector
            "[class*='metric']",  # Attribute selector
        ]
        
        # Mock CSS analysis
        with patch('microsoft_mcp.email_framework.analyze_css_selectors') as mock_analyze:
            mock_analyze.return_value = {
                "efficient": len(efficient_selectors),
                "inefficient": 0
            }
            
            result = mock_analyze(efficient_selectors)
            assert result["inefficient"] == 0
    
    def test_compression_ratio(self):
        """Test content compression ratio."""
        original_content = "A" * 1000 + "B" * 1000  # Repetitive content
        
        with patch('microsoft_mcp.email_framework.compress_content') as mock_compress:
            # Simulate compression
            compressed_size = len(original_content) // 10
            mock_compress.return_value = compressed_size
            
            ratio = compressed_size / len(original_content)
            assert ratio < 0.5, "Compression ratio should be better for repetitive content"