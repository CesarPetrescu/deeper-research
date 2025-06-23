#!/usr/bin/env python3
"""
Database management utility for Deep Crawler research reports
"""
import argparse
import sys
from pathlib import Path

# Add the project root to path
sys.path.insert(0, str(Path(__file__).parent))

from deep_crawler import reports_db

def list_reports(limit=20):
    """List recent research reports"""
    reports = reports_db.list_reports(limit=limit)
    
    print(f"Found {len(reports)} recent reports:")
    print("=" * 80)
    
    for report in reports:
        status = "✓ Complete" if report['has_content'] else "✗ Error" if report['has_error'] else "... Processing"
        print(f"{report['id'][:8]}... | {status:12} | {report['created_at']}")
        print(f"  Question: {report['question']}")
        print()

def show_report(research_id):
    """Show details of a specific report"""
    report = reports_db.get_report(research_id)
    
    if not report:
        print(f"Report {research_id} not found")
        return
    
    print(f"Research Report: {research_id}")
    print("=" * 50)
    print(f"Question: {report['question']}")
    print(f"Created: {report['created_at']}")
    print(f"Generated: {report['generated_at']}")
    
    if report['content']:
        print(f"Content: {len(report['content'])} characters")
        print("\nFirst 200 characters:")
        print(report['content'][:200] + "..." if len(report['content']) > 200 else report['content'])
    
    if report['error']:
        print(f"Error: {report['error']}")

def delete_report(research_id):
    """Delete a specific report"""
    if reports_db.delete_report(research_id):
        print(f"Report {research_id} deleted successfully")
    else:
        print(f"Report {research_id} not found")

def cleanup_old(days=30):
    """Clean up old reports"""
    count = reports_db.cleanup_old_reports(days=days)
    print(f"Cleaned up {count} reports older than {days} days")

def stats():
    """Show database statistics"""
    reports = reports_db.list_reports(limit=1000)  # Get all reports
    
    total = len(reports)
    completed = sum(1 for r in reports if r['has_content'])
    errors = sum(1 for r in reports if r['has_error'])
    processing = total - completed - errors
    
    print("Database Statistics:")
    print("=" * 30)
    print(f"Total reports: {total}")
    print(f"Completed: {completed}")
    print(f"Errors: {errors}")
    print(f"Processing: {processing}")
    
    if total > 0:
        print(f"Success rate: {completed/total*100:.1f}%")

def main():
    parser = argparse.ArgumentParser(description='Manage Deep Crawler research database')
    parser.add_argument('--list', '-l', action='store_true', help='List recent reports')
    parser.add_argument('--show', '-s', help='Show specific report by ID')
    parser.add_argument('--delete', '-d', help='Delete specific report by ID')
    parser.add_argument('--cleanup', type=int, metavar='DAYS', help='Clean up reports older than N days')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    parser.add_argument('--limit', type=int, default=20, help='Limit for list command')
    
    args = parser.parse_args()
    
    if args.list:
        list_reports(limit=args.limit)
    elif args.show:
        show_report(args.show)
    elif args.delete:
        delete_report(args.delete)
    elif args.cleanup is not None:
        cleanup_old(days=args.cleanup)
    elif args.stats:
        stats()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
