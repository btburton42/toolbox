#!/usr/bin/env python3
"""
Find all files with tags on a macOS external drive and log their metadata.
Optionally copy tagged files to a local directory.
"""

import os
import sys
import xattr
import argparse
import shutil
from pathlib import Path
from datetime import datetime

def get_file_tags(file_path):
    """
    Extract tags from a file's extended attributes.
    Returns a list of tag names.
    """
    try:
        x = xattr.xattr(file_path)
        # macOS stores tags in the com.apple.metadata:_kMDItemUserTags extended attribute
        tags_data = x.get('com.apple.metadata:_kMDItemUserTags')
        if tags_data:
            # Tags are stored as a plist in the extended attribute
            import plistlib
            tags = plistlib.loads(tags_data)
            return tags if isinstance(tags, list) else [tags]
    except (OSError, KeyError):
        pass
    return []

def get_file_metadata(file_path):
    """
    Get comprehensive metadata for a file.
    """
    try:
        stat_info = os.stat(file_path)
        return {
            'size': stat_info.st_size,
            'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            'created': datetime.fromtimestamp(stat_info.st_birthtime).isoformat() if hasattr(stat_info, 'st_birthtime') else 'N/A',
            'mode': oct(stat_info.st_mode),
            'owner_uid': stat_info.st_uid,
            'group_gid': stat_info.st_gid,
        }
    except OSError:
        return {}

def find_all_tagged_files(directory, tag_filter=None):
    """
    Find all files in directory that have any tags.
    If tag_filter is specified, only return files with that tag.
    Yields (absolute_path, relative_path, tags, metadata) tuples.
    """
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            abs_path = os.path.join(root, file)
            tags = get_file_tags(abs_path)
            
            # Filter by tag if specified
            if tag_filter:
                if not any(tag_filter in tag for tag in tags):
                    continue
            else:
                if not tags:  # Only yield if file has tags
                    continue
            
            rel_path = os.path.relpath(abs_path, directory)
            metadata = get_file_metadata(abs_path)
            yield abs_path, rel_path, tags, metadata

def format_size(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def copy_file(src_path, dest_base, rel_path):
    """
    Copy a file from source to destination, maintaining relative directory structure.
    Returns True if successful, False otherwise.
    """
    dest_path = os.path.join(dest_base, rel_path)
    dest_dir = os.path.dirname(dest_path)
    
    try:
        # Create destination directories if they don't exist
        os.makedirs(dest_dir, exist_ok=True)
        
        # Copy the file
        shutil.copy2(src_path, dest_path)
        return True
    except Exception as e:
        print(f"  ✗ Error copying: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description='Find and optionally copy tagged files from external drive')
    parser.add_argument('--copy', type=str, help='Copy tagged files to this local directory')
    parser.add_argument('--dryrun', type=str, help='Dry-run mode: print what would be copied without actually copying')
    parser.add_argument('--tag', type=str, help='Filter by specific tag (e.g., "Blue", "Red")')
    args = parser.parse_args()
    
    drive_path = "/Volumes/BIG_ORANGE"
    
    if not os.path.exists(drive_path):
        print(f"Error: Drive not found at {drive_path}", file=sys.stderr)
        sys.exit(1)
    
    # Resolve copy destination if provided
    copy_dest = None
    is_dryrun = False
    if args.copy:
        copy_dest = os.path.abspath(args.copy)
        if not os.path.exists(copy_dest):
            print(f"Creating destination directory: {copy_dest}")
            try:
                os.makedirs(copy_dest, exist_ok=True)
            except Exception as e:
                print(f"Error creating destination directory: {e}", file=sys.stderr)
                sys.exit(1)
    elif args.dryrun:
        copy_dest = os.path.abspath(args.dryrun)
        is_dryrun = True
    
    print(f"Scanning for all tagged files in {drive_path}\n")
    if args.tag:
        print(f"Filtering for tag: {args.tag}\n")
    if copy_dest and is_dryrun:
        print(f"[DRY-RUN] Files would be copied to: {copy_dest}\n")
        print("Files to be copied:\n")
    elif copy_dest:
        print(f"Files will be copied to: {copy_dest}\n")
    print("=" * 80)
    
    found_count = 0
    copied_count = 0
    for abs_path, rel_path, tags, metadata in find_all_tagged_files(drive_path, tag_filter=args.tag):
        found_count += 1
        print(f"\n[File {found_count}]")
        print(f"  Path: {rel_path}")
        print(f"  Tags: {', '.join(tags)}")
        if metadata:
            print(f"  Size: {format_size(metadata.get('size', 0))}")
            print(f"  Modified: {metadata.get('modified', 'N/A')}")
            print(f"  Created: {metadata.get('created', 'N/A')}")
            print(f"  Mode: {metadata.get('mode', 'N/A')}")
            print(f"  Owner UID: {metadata.get('owner_uid', 'N/A')}")
            print(f"  Group GID: {metadata.get('group_gid', 'N/A')}")
        
        # Handle copy or dry-run
        if copy_dest:
            if is_dryrun:
                filename = os.path.basename(abs_path)
                new_rel_path = os.path.join(args.dryrun, rel_path)
                print(f"  ({filename!r}, {new_rel_path!r})")
                copied_count += 1
            else:
                if copy_file(abs_path, copy_dest, rel_path):
                    print(f"  ✓ Copied")
                    copied_count += 1
                else:
                    print(f"  ✗ Failed to copy")
        
        print("-" * 80)
    
    print(f"\nFound {found_count} file(s) with tags")
    if args.tag:
        print(f"(filtered by tag: {args.tag})")
    if copy_dest:
        if is_dryrun:
            print(f"[DRY-RUN] Would copy {copied_count} file(s) to {args.dryrun}")
        else:
            print(f"Successfully copied {copied_count} file(s) to {copy_dest}")

if __name__ == "__main__":
    main()
