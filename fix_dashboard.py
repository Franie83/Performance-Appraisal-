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

    {% if current_user.has_role("ADMIN") %}
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
                                    <p>Create predefined test users for all roles</p>
                                    <button type="button" class="btn btn-primary" id="seedBtn">Seed All Test Users</button>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card bg-light">
                                <div class="card-body">
                                    <h5>Create Custom User</h5>
                                    <p>Create a new user manually</p>
                                    <button type="button" class="btn btn-secondary" id="createUserBtn">Create User</button>
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
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Username</th>
                                    <th>Email</th>
                                    <th>Role</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for user in users %}
                                <tr>
                                    <td>{{ user.id }}</td>
                                    <td>{{ user.username }}</td>
                                    <td>{{ user.email }}</td>
                                    <td>{{ user.role }}</td>
                                    <td>{% if user.is_active %}Active{% else %}Inactive{% endif %}</td>
                                    <td><button class="btn btn-sm btn-danger delete-btn" data-user-id="{{ user.id }}">Delete</button></td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% endif %}
</div>

<!-- Modal for Create User -->
<div class="modal fade" id="createUserModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header bg-primary text-white">
                <h5 class="modal-title">Create New User</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div class="mb-3">
                    <label class="form-label">Username</label>
                    <input type="text" class="form-control" id="username" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Password</label>
                    <input type="password" class="form-control" id="password" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Role</label>
                    <select class="form-control" id="role">
                        <option value="ADMIN">ADMIN</option>
                        <option value="HR">HR</option>
                        <option value="OFFICER">OFFICER</option>
                        <option value="REPORTING_OFFICER">REPORTING OFFICER</option>
                        <option value="COUNTERSIGNING_OFFICER">COUNTERSIGNING OFFICER</option>
                    </select>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" id="modalCreateBtn">Create User</button>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener("DOMContentLoaded", function() {
    var seedBtn = document.getElementById("seedBtn");
    if(seedBtn) {
        seedBtn.addEventListener("click", function() {
            if(confirm("This will create all test users. Continue?")) {
                fetch("/admin/seed-users", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"}
                })
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    alert(data.message);
                    if(data.success) location.reload();
                })
                .catch(function(error) { alert("Error: " + error); });
            }
        });
    }

    var createUserBtn = document.getElementById("createUserBtn");
    if(createUserBtn) {
        createUserBtn.addEventListener("click", function() {
            document.getElementById("username").value = "";
            document.getElementById("email").value = "";
            document.getElementById("password").value = "";
            document.getElementById("role").value = "OFFICER";
            var modal = new bootstrap.Modal(document.getElementById("createUserModal"));
            modal.show();
        });
    }

    var modalCreateBtn = document.getElementById("modalCreateBtn");
    if(modalCreateBtn) {
        modalCreateBtn.addEventListener("click", function() {
            var username = document.getElementById("username").value;
            var email = document.getElementById("email").value;
            var password = document.getElementById("password").value;
            var role = document.getElementById("role").value;
                alert("Please fill in all fields");
                return;
            }
            var userData = {
                username: username,
                email: email,
                password: password,
                role: role
            };
            fetch("/admin/create-user", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(userData)
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                alert(data.message);
                if(data.success) {
                    var modal = bootstrap.Modal.getInstance(document.getElementById("createUserModal"));
                    modal.hide();
                    location.reload();
                }
            })
            .catch(function(error) { alert("Error: " + error); });
        });
    }

    var deleteBtns = document.querySelectorAll(".delete-btn");
        deleteBtns[i].addEventListener("click", function() {
            var userId = this.getAttribute("data-user-id");
            if(confirm("Delete this user?")) {
                fetch("/admin/delete-user/" + userId, { method: "DELETE" })
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    alert(data.message);
                    if(data.success) location.reload();
                })
                .catch(function(error) { alert("Error: " + error); });
            }
        });
    }
});
</script>
{% endblock %}'''

with open('app/templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Dashboard template created successfully!')
with open('app/templates/dashboard.html', 'w', encoding='utf-8') as f:
