import os
import json
import subprocess
import tempfile
from flask import Flask, jsonify, request
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

@app.route('/api/ping', methods=['GET'])
def ping_hosts():
    """Run ansible ping module on all hosts and return results"""
    try:
        result = subprocess.run(
            ['ansible', 'all', '-m', 'ping'],
            capture_output=True,
            text=True
        )
        
        # Parse the ansible output
        output = result.stdout
        lines = output.strip().split('\n')
        
        hosts_status = []
        current_host = None
        current_data = ""
        
        for line in lines:
            if line.startswith('192.168.31.'):
                if current_host and current_data:
                    try:
                        status_data = json.loads(current_data)
                        hosts_status.append({
                            'host': current_host,
                            'status': 'success' if status_data.get('ping') == 'pong' else 'failed',
                            'data': status_data
                        })
                    except json.JSONDecodeError:
                        hosts_status.append({
                            'host': current_host,
                            'status': 'failed',
                            'error': current_data
                        })
                
                current_host = line.split(' ')[0]
                current_data = ""
            else:
                current_data += line
        
        # Process the last host
        if current_host and current_data:
            try:
                status_data = json.loads(current_data)
                hosts_status.append({
                    'host': current_host,
                    'status': 'success' if status_data.get('ping') == 'pong' else 'failed',
                    'data': status_data
                })
            except json.JSONDecodeError:
                hosts_status.append({
                    'host': current_host,
                    'status': 'failed',
                    'error': current_data
                })
        
        return jsonify({
            'success': True,
            'hosts': hosts_status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hosts', methods=['GET'])
def get_hosts():
    """Get the list of hosts from Ansible hosts file"""
    try:
        hosts = []
        with open('/etc/ansible/hosts', 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if line and not line.startswith('[') and not line.startswith('#'):
                if 'ansible_ssh_host' in line:
                    parts = line.split()
                    host_info = {}
                    host_info['name'] = parts[0]
                    
                    for part in parts[1:]:
                        if '=' in part:
                            key, value = part.split('=')
                            host_info[key] = value
                    
                    hosts.append(host_info)
        
        return jsonify({
            'success': True,
            'hosts': hosts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hosts', methods=['POST'])
def add_host():
    """Add a new host to Ansible hosts file"""
    try:
        data = request.json
        if not data or not data.get('hostname') or not data.get('ip'):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
            
        hostname = data['hostname']
        ip = data['ip']
        username = data.get('username', 'root')
        
        host_line = f"{ip} ansible_ssh_host={ip} ansible_ssh_user={username} hostname={hostname}\n"
        
        # Read the current hosts file
        with open('/etc/ansible/hosts', 'r') as f:
            lines = f.readlines()
        
        # Find where to insert the new host
        insert_index = 0
        for i, line in enumerate(lines):
            if line.strip() == '[hosts]':
                insert_index = i + 1
                break
        
        # Insert the new host
        lines.insert(insert_index, host_line)
        
        # Write back to the file
        with open('/etc/ansible/hosts', 'w') as f:
            f.writelines(lines)
        
        return jsonify({
            'success': True,
            'message': f'Host {hostname} ({ip}) added successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hosts/<ip>', methods=['DELETE'])
def delete_host(ip):
    """Delete a host from Ansible hosts file"""
    try:
        # Read the current hosts file
        with open('/etc/ansible/hosts', 'r') as f:
            lines = f.readlines()
        
        # Filter out the host to delete
        new_lines = [line for line in lines if not line.startswith(f"{ip} ")]
        
        # Write back to the file
        with open('/etc/ansible/hosts', 'w') as f:
            f.writelines(new_lines)
        
        return jsonify({
            'success': True,
            'message': f'Host {ip} deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hosts/<ip>', methods=['PUT'])
def update_host(ip):
    """Update a host in Ansible hosts file"""
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        # Read the current hosts file
        with open('/etc/ansible/hosts', 'r') as f:
            lines = f.readlines()
        
        # Find and update the host
        for i, line in enumerate(lines):
            if line.startswith(f"{ip} "):
                new_ip = data.get('ip', ip)
                hostname = data.get('hostname', '')
                username = data.get('username', 'root')
                
                if not hostname:
                    # Extract hostname from existing line
                    for part in line.split():
                        if part.startswith('hostname='):
                            hostname = part.split('=')[1]
                            break
                
                lines[i] = f"{new_ip} ansible_ssh_host={new_ip} ansible_ssh_user={username} hostname={hostname}\n"
                break
        
        # Write back to the file
        with open('/etc/ansible/hosts', 'w') as f:
            f.writelines(lines)
        
        return jsonify({
            'success': True,
            'message': f'Host {ip} updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system-info', methods=['GET'])
def get_system_info():
    """Get system information using Ansible setup module (with -o for easier parsing)"""
    try:
        result = subprocess.run(
            ['ansible', 'all', '-m', 'setup', '-o'],
            capture_output=True,
            text=True
        )
        output = result.stdout
        # 每行格式: host | SUCCESS => { ...json... }
        pattern = re.compile(r'^(\S+) \| SUCCESS => (\{.*\})$', re.MULTILINE)
        hosts_info = []
        for match in pattern.finditer(output):
            host = match.group(1)
            try:
                info_data = json.loads(match.group(2))
                facts = info_data.get('ansible_facts', {})
                host_info = {
                    'host': host,
                    'hostname': facts.get('ansible_hostname', ''),
                    'os': facts.get('ansible_distribution', '') + ' ' + facts.get('ansible_distribution_version', ''),
                    'cpu_cores': facts.get('ansible_processor_cores', 0),
                    'memory_total': facts.get('ansible_memtotal_mb', 0),
                    'disk_total': sum([int(item.get('size_total', 0)) // (1024*1024*1024) for item in facts.get('ansible_mounts', [])]),
                    'uptime': facts.get('ansible_uptime_seconds', 0) // 3600,
                    'status': 'online'
                }
                hosts_info.append(host_info)
            except Exception as e:
                hosts_info.append({
                    'host': host,
                    'status': 'error',
                    'error': f'Failed to parse system information: {str(e)}',
                    'raw': match.group(2)
                })
        return jsonify({
            'success': True,
            'hosts': hosts_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/resource-monitor', methods=['GET'])
def get_resource_monitor():
    """Run ansible playbook to monitor resources"""
    try:
        # Create a temporary file to store the JSON output
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            temp_path = tmp.name
        
        # Run the ansible playbook with JSON output
        result = subprocess.run(
            ['ansible-playbook', '/etc/ansible/resource_monitor.yml', '-v'],
            capture_output=True,
            text=True
        )
        
        # Parse the output to extract the resource reports
        output = result.stdout
        
        # Extract the resource_report debug output
        resources = []
        host_data = {}
        current_host = None
        
        for line in output.split('\n'):
            # Detect host
            if "TASK [setup]" in line and "=>" in line:
                host_match = line.split("=>")[0].strip()
                if host_match:
                    current_host = host_match
                    host_data[current_host] = {}
            
            # Look for the resource report debug output
            if "TASK [显示资源报告]" in line:
                in_debug = True
            
            # Extract the resource report data
            if current_host and "resource_report" in line and ":" in line:
                try:
                    # Try to parse the line as JSON if it contains the resource report
                    if "{" in line and "}" in line:
                        json_str = line.split(":", 1)[1].strip()
                        report_data = json.loads(json_str)
                        resources.append({
                            'host': current_host,
                            'data': report_data
                        })
                except json.JSONDecodeError:
                    pass
        
        # If we couldn't parse the output, return the raw output for debugging
        if not resources:
            return jsonify({
                'success': False,
                'error': 'Failed to parse resource monitor output',
                'raw_output': output,
                'raw_error': result.stderr
            }), 500
        
        return jsonify({
            'success': True,
            'resources': resources
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 