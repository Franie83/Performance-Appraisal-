import os 
 
content = '''{% extends "base.html" %} 
 
{% block content %} 
<div class="container"> 
    <div class="row"> 
        <div class="col-12"> 
            <div class="card"> 
                <div class="card-header bg-primary text-white"> 
                    <h4>Dashboard</h4> 
                </div> 
                <div class="card-body"> 
                    <h5>Welcome, {{ current_user.username }}!</h5> 
                    <p>Role: <span class="badge bg-info">{{ current_user.role }}</span></p> 
                </div> 
            </div> 
        </div> 
    </div> 
 
    {% if current_user.has_role('ADMIN') %} 
    <div class="row mt-4"> 
        <div class="col-12"> 
            <div class="card"> 
                <div class="card-header bg-success text-white"> 
                    <h5>User Management</h5> 
                </div> 
                <div class="card-body"> 
                    <div class="row"> 
                        <div class="col-md-6"> 
                            <div class="card bg-light"> 
                                <div class="card-body"> 
                                    <h5>Seed Test Users</h5> 
                                    <button onclick="seedUsers()" class="btn btn-primary">Seed All Test Users</button> 
                                    <div id="seedResult" class="mt-2"></div> 
                                </div> 
                            </div> 
                        </div> 
                        <div class="col-md-6"> 
                            <div class="card bg-light"> 
                                <div class="card-body"> 
                                    <h5>Create Custom User</h5> 
                                    <button class="btn btn-secondary" data-bs-toggle="modal" data-bs-target="#createUserModal">Create User</button> 
                                </div> 
                            </div> 
                        </div> 
                    </div> 
                </div> 
            </div> 
        </div> 
    </div> 
 
    <div class="row mt-4"> 
        <div class="col-12"> 
            <div class="card"> 
                <div class="card-header bg-info text-white"> 
                    <h5>System Users</h5> 
                </div> 
                <div class="card-body"> 
                    <table class="table table-striped"> 
                        <thead> 
                        </thead> 
                        <tbody> 
                            {% for user in users %} 
                            <tr> 
                                <td>{{ user.id }}</td> 
                                <td>{{ user.username }}</td> 
                                <td>{{ user.email }}</td> 
                                <td>{{ user.role }}</td> 
                                <td>{% if user.is_active %}Active{% else %}Inactive{% endif %}</td> 
                                <td><button class="btn btn-sm btn-danger" onclick="deleteUser({{ user.id }})">Delete</button></td> 
                            </tr> 
                            {% endfor %} 
                        </tbody> 
                    </table> 
                </div> 
            </div> 
        </div> 
    </div> 
    {% endif %} 
</div> 
 
<!-- Modal --> 
<div class="modal fade" id="createUserModal" tabindex="-1"> 
    <div class="modal-dialog"> 
        <div class="modal-content"> 
            <div class="modal-header"><h5>Create User</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div> 
            <div class="modal-body"> 
                <input type="text" id="username" class="form-control mb-2" placeholder="Username"> 
                <input type="email" id="email" class="form-control mb-2" placeholder="Email"> 
                <input type="password" id="password" class="form-control mb-2" placeholder="Password"> 
                <select id="role" class="form-control mb-2"> 
                    <option value="OFFICER">OFFICER</option> 
                    <option value="ADMIN">ADMIN</option> 
                    <option value="HR">HR</option> 
                    <option value="REPORTING_OFFICER">REPORTING OFFICER</option> 
                    <option value="COUNTERSIGNING_OFFICER">COUNTERSIGNING OFFICER</option> 
                </select> 
            </div> 
            <div class="modal-footer"> 
                <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button> 
                <button class="btn btn-primary" onclick="createUser()">Create</button> 
            </div> 
        </div> 
    </div> 
</div> 
 
<script> 
function seedUsers() { 
    fetch('/admin/seed-users', {method:'POST'}) 
    .then(r=
    .then(d=;if(d.success)location.reload();}); 
} 
function createUser() { 
    var data = { 
        username: document.getElementById('username').value, 
        email: document.getElementById('email').value, 
        password: document.getElementById('password').value, 
        role: document.getElementById('role').value 
    }; 
    fetch('/admin/create-user', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}) 
    .then(r=
    .then(d=;if(d.success)location.reload();}); 
} 
function deleteUser(id) { 
    if(confirm('Delete?')) fetch('/admin/delete-user/'+id,{method:'DELETE'}).then(r=;if(d.success)location.reload();}); 
} 
</script> 
{% endblock %}''' 
 
with open('app/templates/dashboard.html', 'w') as f: 
    f.write(content) 
print('Template created successfully!') 
